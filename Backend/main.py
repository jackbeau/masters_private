"""
Main entry point for the application. Starts the Python gRPC server, Node.js
REST server, and Tkinter GUI.
"""

import json
import logging
from multiprocessing import Process
import subprocess
import sys
from gui.app import App
from async_tkinter_loop import async_mainloop

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def start_python_grpc_server(settings):
    """
    Start the Python gRPC server with the provided settings.

    Args:
        settings (dict): Configuration settings for the gRPC server.
    """
    logging.info("Starting Python gRPC server with settings: %s", settings)
    subprocess.run(
        [
            sys.executable,
            "server/grpc/python/server/server.py",
            json.dumps(settings),
        ]
    )


def start_api_server():
    """
    Start the Node.js REST server.
    """
    logging.info("Starting Node.js REST server.")
    subprocess.run(["node", "server/server.js"])


if __name__ == "__main__":
    # Load settings from settings.json
    logging.info("Loading settings from settings.json.")
    with open("settings.json", "r") as f:
        settings = json.load(f)

    # Start the Python gRPC server
    logging.info("Starting the Python gRPC server.")
    grpc_process = Process(target=start_python_grpc_server, args=(settings,))
    grpc_process.start()

    # Start the Node.js REST server
    logging.info("Starting the Node.js REST server.")
    api_process = Process(target=start_api_server)
    api_process.start()

    # Start Tkinter UI
    logging.info("Starting the Tkinter GUI.")
    app = App()
    async_mainloop(app)

    # If the app is closed, stop the servers
    logging.info("Shutting down servers.")
    grpc_process.terminate()
    api_process.terminate()
    logging.info("Servers shut down. Exiting application.")
    quit()
