from concurrent import futures
import grpc
import subprocess
import sys
import json

# Adjust the import paths
import service_pb2
import service_pb2_grpc

class ScriptService(service_pb2_grpc.ScriptServiceServicer):

    def AddMargin(self, request, context):
        file_path = request.file_path
        margin_side = request.margin_side

        result = subprocess.run(
            [sys.executable, 'server/grpc/python/add_margin.py', file_path, margin_side],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AddMarginResponse()

        response = json.loads(result.stdout)
        return service_pb2.AddMarginResponse(file_path=response['file_path'])

    def PerformOCR(self, request, context):
        file_path = request.file_path

        result = subprocess.run(
            [sys.executable, 'server/grpc/python/perform_ocr.py', file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.OCRResponse()

        response = json.loads(result.stdout)
        return service_pb2.OCRResponse(text=response['text'])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ScriptServiceServicer_to_server(ScriptService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('gRPC server running on port 50051...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()