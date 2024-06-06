"""
Author: Jack Beaumont
Date: 06/06/2024

This module provides a manager for an MQTT broker using embedded HiveMQ.
It starts, stops, and restarts the broker and ensures the broker's status
can be checked.

Classes:
    MQTTBrokerManager: Manages the lifecycle of the MQTT broker.
    MQTTBroker: Represents the MQTT broker and handles its operations.
"""

import time
import threading
import logging
from jpype import startJVM, JClass
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MQTTBrokerManager:
    """
    Manages the lifecycle of an embedded MQTT broker.

    Attributes:
        mqtt_config_folder (str): Path to the MQTT configuration folder.
        class_path (str): Classpath for the JVM.
    """

    def __init__(
        self,
        mqtt_config_folder="broker/mqtt_embedded_conf",
        class_path="broker/jar/*",
    ):
        self.MQTT_CONFIG_FOLDER = mqtt_config_folder
        self.CLASS_PATH = class_path
        self.java_execution_completed = threading.Event()
        self.mqtt_broker = None

    def start(self):
        """Starts the MQTT broker."""
        self.mqtt_broker = MQTTBroker(
            self.MQTT_CONFIG_FOLDER,
            self.CLASS_PATH,
            self.java_execution_completed,
        )
        self.mqtt_broker.start()
        self.java_execution_completed.wait()
        logging.info("MQTT broker started.")

    def stop(self):
        """Stops the MQTT broker if it is running."""
        if self.mqtt_broker:
            self.mqtt_broker.stop()
            logging.info("MQTT broker stopped.")
        else:
            logging.warning("MQTT broker is not running.")

    def restart(self):
        """Restarts the MQTT broker."""
        if self.mqtt_broker:
            self.mqtt_broker.restart()
            self.java_execution_completed.wait()
            logging.info("MQTT broker restarted.")
        else:
            logging.warning("MQTT broker is not running.")

    def is_running(self):
        """Checks if the MQTT broker is running.

        Returns:
            bool: True if the broker is running, False otherwise.
        """
        if self.mqtt_broker:
            return self.mqtt_broker.is_running()
        else:
            logging.warning("MQTT broker is not running.")
            return False


class MQTTBroker(threading.Thread):
    """
    Represents the embedded MQTT broker and handles its operations.

    Attributes:
        mqtt_config_folder (str): Path to the MQTT configuration folder.
        class_path (str): Classpath for the JVM.
        java_execution_completed (threading.Event): Event to signal completion
                                                    of Java execution.
    """

    def __init__(
        self, mqtt_config_folder, class_path, java_execution_completed
    ):
        super().__init__()
        self.MQTT_CONFIG_FOLDER = mqtt_config_folder
        self.CLASS_PATH = class_path
        self.java_execution_completed = java_execution_completed
        startJVM("-ea", classpath=[self.CLASS_PATH])

    def run(self):
        """Starts the MQTT broker instance."""
        try:
            self.java_execution_completed.clear()
            EmbeddedMQTT = JClass("broker.EmbeddedMQTT")
            self.mqtt_instance = EmbeddedMQTT(self.MQTT_CONFIG_FOLDER)
            self._start_mqtt_instance()
            self.java_execution_completed.set()
        except Exception as e:
            logging.error("Error starting MQTT broker: %s", e)
            self.java_execution_completed.set()

    def _start_mqtt_instance(self):
        """Internal method to start the MQTT broker instance."""
        try:
            self.java_execution_completed.clear()
            logging.info("Starting HiveMQ server...")
            self.mqtt_instance.startServer()
            logging.info("HiveMQ server running...")
            self.java_execution_completed.set()
        except Exception as e:
            logging.error("Error starting HiveMQ server: %s", e)
            self.java_execution_completed.set()

    def stop(self):
        """Stops the MQTT broker instance."""
        try:
            self.java_execution_completed.clear()
            logging.info("Stopping HiveMQ server...")
            self.mqtt_instance.stopServer()
            logging.info("HiveMQ server stopped.")
            self.java_execution_completed.set()
        except Exception as e:
            logging.error("Error stopping HiveMQ server: %s", e)
            self.java_execution_completed.set()

    def restart(self):
        """Restarts the MQTT broker instance."""
        try:
            logging.info("Restarting HiveMQ server...")
            self.java_execution_completed.clear()
            if self.is_running():
                self.mqtt_instance.stopServer()
            self.mqtt_instance.startServer()
            logging.info("HiveMQ server restarted.")
            self.java_execution_completed.set()
        except Exception as e:
            logging.error("Error restarting HiveMQ server: %s", e)
            self.java_execution_completed.set()

    def is_running(self):
        """Checks if the MQTT broker instance is running.

        Returns:
            bool: True if the broker is running, False otherwise.
        """
        try:
            return self.mqtt_instance.isServerRunning()
        except Exception as e:
            logging.error("Error checking HiveMQ server status: %s", e)
            return False


if __name__ == "__main__":
    mqtt_manager = MQTTBrokerManager()
    mqtt_manager.start()

    # Wait for some time (for demonstration purposes)
    time.sleep(10)

    # Stop the MQTT broker
    mqtt_manager.stop()
