"""
Author: Jack Beaumont
Date: 06/06/2024

This module implements a gRPC service for managing various script processing
tasks including adding margins, performing OCR, and controlling background
processes like speech-to-script pointer and performer tracker.
"""

from concurrent import futures
import grpc
import subprocess
import sys
import json
from multiprocessing import Process, Queue
import os
import logging

import service_pb2
import service_pb2_grpc

# Ensure the module path is correctly set
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mqtt_controller.mqtt_controller import MQTTController  # noqa: E402
from speech_to_script_pointer.main import SpeechToScriptPointer  # noqa: E402
from performer_tracker.performer_tracker import PerformerTracker  # noqa: E402

OUTPUT_DIR = "server/storage/pdfs/"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ScriptService(service_pb2_grpc.ScriptServiceServicer):
    def __init__(self, settings):
        """
        Initializes the ScriptService with settings.

        Parameters:
        settings (dict): Configuration settings for the service.
        """
        self.speech_to_script_pointer_process = None
        self.performer_tracker_process = None
        self.speech_to_script_pointer_status_queue = Queue()
        self.performer_tracker_status_queue = Queue()
        self.settings = settings

        # Initialize statuses
        self.rpc_status = "Running"
        self.speech_to_script_pointer_status = "Stopped"
        self.performer_tracker_status = "Stopped"

    def AddMargin(self, request, context):
        """
        Adds a margin to a PDF file.

        Parameters:
        request (AddMarginRequest): The request containing file_path and
                                    margin_side.
        context (grpc.ServicerContext): The context for the gRPC call.

        Returns:
        AddMarginResponse: The response containing the file path of the
                           modified PDF.
        """
        file_path = request.file_path
        margin_side = request.margin_side

        result = subprocess.run(
            [
                sys.executable,
                "server/grpc/python/pdf_utils/add_margin.py",
                file_path,
                margin_side,
                OUTPUT_DIR,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AddMarginResponse()

        try:
            response = json.loads(result.stdout)
            return service_pb2.AddMarginResponse(
                file_path=response["file_path"]
            )
        except json.JSONDecodeError as e:
            context.set_details(
                f"JSON decode error: {e} - Output was: {result.stdout}"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AddMarginResponse()

    def PerformOCR(self, request, context):
        """
        Performs OCR on a PDF file.

        Parameters:
        request (OCRRequest): The request containing the file path.
        context (grpc.ServicerContext): The context for the gRPC call.

        Returns:
        OCRResponse: The response containing the file path of the OCR
                     processed PDF.
        """
        file_path = request.file_path

        result = subprocess.run(
            [
                sys.executable,
                "server/grpc/python/pdf_utils/perform_ocr/__init__.py",
                file_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.OCRResponse()

        response = json.loads(result.stdout)
        return service_pb2.OCRResponse(file_path=response["file_path"])

    def StartSpeechToScriptPointer(self, request, context):
        """
        Starts the SpeechToScriptPointer process.

        Parameters:
        request (StartRequest): The request to start the process.
        context (grpc.ServicerContext): The context for the gRPC call.

        Returns:
        StartResponse: The response indicating the success of the operation.
        """
        if (
            self.speech_to_script_pointer_process
            and self.speech_to_script_pointer_process.is_alive()
        ):
            return service_pb2.StartResponse(success=False)

        self.speech_to_script_pointer_process = Process(
            target=self.run_speech_to_script_pointer,
            args=(self.speech_to_script_pointer_status_queue, self.settings),
        )
        self.speech_to_script_pointer_process.start()
        status = (
            self.speech_to_script_pointer_status_queue.get()
        )  # Wait for acknowledgment
        self.speech_to_script_pointer_status = status
        return service_pb2.StartResponse(success=status == "Started")

    def StopSpeechToScriptPointer(self, request, context):
        """
        Stops the SpeechToScriptPointer process.

        Parameters:
        request (StopRequest): The request to stop the process.
        context (grpc.ServicerContext): The context for the gRPC call.

        Returns:
        StopResponse: The response indicating the success of the operation.
        """
        if (
            self.speech_to_script_pointer_process
            and self.speech_to_script_pointer_process.is_alive()
        ):
            self.speech_to_script_pointer_process.terminate()
            self.speech_to_script_pointer_process.join()
            self.speech_to_script_pointer_status_queue.put(
                "Stopped"
            )  # Ensure stopped status is put in the queue
            status = (
                self.speech_to_script_pointer_status_queue.get()
            )  # Wait for acknowledgment
            self.speech_to_script_pointer_status = status
            return service_pb2.StopResponse(success=status == "Stopped")
        return service_pb2.StopResponse(success=False)

    def run_speech_to_script_pointer(self, status_queue, settings):
        """
        Runs the SpeechToScriptPointer process.

        Parameters:
        status_queue (Queue): The queue for communicating the status.
        settings (dict): Configuration settings for the process.
        """
        try:
            mqtt_controller = MQTTController(
                "0.0.0.0", 1883, "speech_to_script_pointer"
            )
            mqtt_controller.connect()
            speech_to_script_pointer = SpeechToScriptPointer(
                mqtt_controller=mqtt_controller,
                status_queue=status_queue,
                settings=settings,
            )
            speech_to_script_pointer.start()
            status_queue.put("Started")
        except Exception as e:
            logging.error(f"Failed to start SpeechToScriptPointer: {e}")
            status_queue.put("failed")

    def StartPerformerTracker(self, request, context):
        """
        Starts the PerformerTracker process.

        Parameters:
        request (StartRequest): The request to start the process.
        context (grpc.ServicerContext): The context for the gRPC call.

        Returns:
        StartResponse: The response indicating the success of the operation.
        """
        if (
            self.performer_tracker_process
            and self.performer_tracker_process.is_alive()
        ):
            return service_pb2.StartResponse(success=False)

        self.performer_tracker_process = Process(
            target=self.run_performer_tracker,
            args=(self.performer_tracker_status_queue, self.settings),
        )
        self.performer_tracker_process.start()
        status = (
            self.performer_tracker_status_queue.get()
        )  # Wait for acknowledgment
        self.performer_tracker_status = status
        return service_pb2.StartResponse(success=status == "Started")

    def StopPerformerTracker(self, request, context):
        """
        Stops the PerformerTracker process.

        Parameters:
        request (StopRequest): The request to stop the process.
        context (grpc.ServicerContext): The context for the gRPC call.

        Returns:
        StopResponse: The response indicating the success of the operation.
        """
        if (
            self.performer_tracker_process
            and self.performer_tracker_process.is_alive()
        ):
            self.performer_tracker_process.terminate()
            self.performer_tracker_process.join()
            self.performer_tracker_status_queue.put(
                "Stopped"
            )  # Ensure stopped status is put in the queue
            status = (
                self.performer_tracker_status_queue.get()
            )  # Wait for acknowledgment
            self.performer_tracker_status = status
            return service_pb2.StopResponse(success=status == "Stopped")
        return service_pb2.StopResponse(success=False)

    def run_performer_tracker(self, status_queue, settings):
        """
        Runs the PerformerTracker process.

        Parameters:
        status_queue (Queue): The queue for communicating the status.
        settings (dict): Configuration settings for the process.
        """
        try:
            performer_tracker = PerformerTracker(
                settings=settings, status_queue=status_queue
            )
            performer_tracker.start()
            status_queue.put("Started")
        except Exception as e:
            logging.error(f"Failed to start PerformerTracker: {e}")
            status_queue.put("failed")

    def GetStatuses(self, request, context):
        """
        Gets the statuses of all processes.

        Parameters:
        request (StatusRequest): The request for statuses.
        context (grpc.ServicerContext): The context for the gRPC call.

        Returns:
        StatusResponse: The response containing the statuses of all processes.
        """
        return service_pb2.StatusResponse(
            rpc_status=self.rpc_status,
            speech_to_script_pointer_status=(
                self.speech_to_script_pointer_status
            ),
            performer_tracker_status=self.performer_tracker_status,
        )


def serve():
    """
    Starts the gRPC server to serve the ScriptService.
    """
    settings = json.loads(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ScriptServiceServicer_to_server(
        ScriptService(settings), server
    )
    server.add_insecure_port("[::]:50051")
    logging.info("gRPC server running on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
