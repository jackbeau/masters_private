from gui.app import App
from async_tkinter_loop import async_mainloop
# from server_backend import ServerBackend
import subprocess
from multiprocessing import Process
import sys

def start_python_grpc_server():
    subprocess.run([sys.executable, 'server/grpc/python/server.py'])

def start_node_graphql_server():
    subprocess.run(['node', 'server/server.js'])

if __name__ == "__main__":
    # Start the Python gRPC server
    grpc_process = Process(target=start_python_grpc_server)
    grpc_process.start()

    # Start the Node.js GraphQL server
    graphql_process = Process(target=start_node_graphql_server)
    graphql_process.start()

    # Start MQTT broker
    # start_mqtt_broker()

    # Initialize server backend
    # server_backend = ServerBackend()

    # Start Tkinter UI
    # app = App(server_backend)
    app = App()
    async_mainloop(app)

    # If the app is closed, stop the MQTT broker
    quit()
