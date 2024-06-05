from concurrent import futures
import grpc
import subprocess
import sys
import json
from multiprocessing import Process, Queue, Manager
import os
import time
from threading import Thread

# Adjust the import paths
import service_pb2
import service_pb2_grpc

# Ensure the module path is correctly set
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mqtt_controller.mqtt_controller import MQTTController
from speech_to_script_pointer.main import SpeechToScriptPointer
# from performer_tracker import PerformerTracker

OUTPUT_DIR = 'server/storage/pdfs/'

class ScriptService(service_pb2_grpc.ScriptServiceServicer):

    def __init__(self, settings):
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
        file_path = request.file_path
        margin_side = request.margin_side

        result = subprocess.run(
            [sys.executable, 'server/grpc/python/pdf_utils/add_margin.py', file_path, margin_side, OUTPUT_DIR],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AddMarginResponse()

        try:
            response = json.loads(result.stdout)
            return service_pb2.AddMarginResponse(file_path=response['file_path'])
        except json.JSONDecodeError as e:
            context.set_details(f"JSON decode error: {e} - Output was: {result.stdout}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AddMarginResponse()

    def PerformOCR(self, request, context):
        file_path = request.file_path

        result = subprocess.run(
            [sys.executable, 'server/grpc/python/pdf_utils/perform_ocr/__init__.py', file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.OCRResponse()

        response = json.loads(result.stdout)
        return service_pb2.OCRResponse(file_path=response['file_path'])

    def StartSpeechToScriptPointer(self, request, context):
        if self.speech_to_script_pointer_process and self.speech_to_script_pointer_process.is_alive():
            return service_pb2.StartResponse(success=False)

        self.speech_to_script_pointer_process = Process(target=self.run_speech_to_script_pointer, args=(self.speech_to_script_pointer_status_queue, self.settings))
        self.speech_to_script_pointer_process.start()
        status = self.speech_to_script_pointer_status_queue.get()  # Wait for acknowledgment
        self.speech_to_script_pointer_status = status
        return service_pb2.StartResponse(success=status == "Started")

    def StopSpeechToScriptPointer(self, request, context):
        if self.speech_to_script_pointer_process and self.speech_to_script_pointer_process.is_alive():
            self.speech_to_script_pointer_process.terminate()
            self.speech_to_script_pointer_process.join()
            self.speech_to_script_pointer_status_queue.put("Stopped")  # Ensure stopped status is put in the queue
            status = self.speech_to_script_pointer_status_queue.get()  # Wait for acknowledgment
            self.speech_to_script_pointer_status = status
            return service_pb2.StopResponse(success=status == "Stopped")
        return service_pb2.StopResponse(success=False)

    def run_speech_to_script_pointer(self, status_queue, settings):
        try:
            mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_script_pointer')
            mqtt_controller.connect()
            speech_to_script_pointer = SpeechToScriptPointer(mqtt_controller=mqtt_controller, status_queue=status_queue, settings=settings)
            speech_to_script_pointer.start()
        except Exception as e:
            status_queue.put("failed")

    def StartPerformerTracker(self, request, context):
        if self.performer_tracker_process and self.performer_tracker_process.is_alive():
            return service_pb2.StartResponse(success=False)

        self.performer_tracker_process = Process(target=self.run_performer_tracker, args=(self.performer_tracker_status_queue, self.settings))
        self.performer_tracker_process.start()
        status = self.performer_tracker_status_queue.get()  # Wait for acknowledgment
        self.performer_tracker_status = status
        return service_pb2.StartResponse(success=status == "Started")

    def StopPerformerTracker(self, request, context):
        if self.performer_tracker_process and self.performer_tracker_process.is_alive():
            self.performer_tracker_process.terminate()
            self.performer_tracker_process.join()
            self.performer_tracker_status_queue.put("Stopped")  # Ensure stopped status is put in the queue
            status = self.performer_tracker_status_queue.get()  # Wait for acknowledgment
            self.performer_tracker_status = status
            return service_pb2.StopResponse(success=status == "Stopped")
        return service_pb2.StopResponse(success=False)

    def run_performer_tracker(self, status_queue, settings):
        try:
            print("hi")
            # performer_tracker = PerformerTracker(status_queue=status_queue, settings=settings)
            # performer_tracker.start()
        except Exception as e:
            status_queue.put("failed")

    def GetStatuses(self, request, context):
        return service_pb2.StatusResponse(
            rpc_status=self.rpc_status,
            speech_to_script_pointer_status=self.speech_to_script_pointer_status,
            performer_tracker_status=self.performer_tracker_status
        )
    
def serve():
    settings = json.loads(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ScriptServiceServicer_to_server(ScriptService(settings), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('gRPC server running on port 50051...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
