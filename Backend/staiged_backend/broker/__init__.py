import time
import threading
from jpype import startJVM, JClass
from dotenv import load_dotenv
import os

load_dotenv()

class MQTTBrokerManager:
    def __init__(self, mqtt_config_folder="broker/mqtt_embedded_conf", class_path="broker/jar/*"):
        self.MQTT_CONFIG_FOLDER = mqtt_config_folder
        self.CLASS_PATH = class_path
        self.java_execution_completed = threading.Event()
        self.mqtt_broker = None

    def start(self):
        self.mqtt_broker = MQTTBroker(self.MQTT_CONFIG_FOLDER, self.CLASS_PATH, self.java_execution_completed)
        self.mqtt_broker.start()
        self.java_execution_completed.wait()
        print("MQTT broker started.")

    def stop(self):
        if self.mqtt_broker:
            self.mqtt_broker.stop()
            print("MQTT broker stopped.")
        else:
            print("MQTT broker is not running.")

    def restart(self):
        self.mqtt_broker.restart()
        self.java_execution_completed.wait()

    def is_running(self):
        if self.mqtt_broker:
            return self.mqtt_broker.is_running()
        else:
            print("MQTT broker is not running.")
            return False


class MQTTBroker(threading.Thread):
    def __init__(self, mqtt_config_folder, class_path,
                 java_execution_completed):
        super().__init__()
        self.MQTT_CONFIG_FOLDER = mqtt_config_folder
        self.CLASS_PATH = class_path
        self.java_execution_completed = java_execution_completed
        startJVM("-ea", classpath=[self.CLASS_PATH])

    def run(self):
        try:
            self.java_execution_completed.clear()
            EmbeddedMQTT = JClass("broker.EmbeddedMQTT")
            self.mqtt_instance = EmbeddedMQTT(self.MQTT_CONFIG_FOLDER)
            self._start_mqtt_instance()
            self.java_execution_completed.set()
        except Exception as e:
            print("Error:", e)

    def _start_mqtt_instance(self):
        try:
            self.java_execution_completed.clear()
            print("Starting HiveMQ server...")
            self.mqtt_instance.startServer()
            print("HiveMQ server running...")
            self.java_execution_completed.set()
        except Exception as e:
            print("Error:", e)
            self.java_execution_completed.set()

    def stop(self):
        try:
            self.java_execution_completed.clear()
            print("Stopping HiveMQ server...")
            self.mqtt_instance.stopServer()
            print("HiveMQ server stopped.")
            self.java_execution_completed.set()
        except Exception as e:
            print("Error:", e)
            self.java_execution_completed.set()

    def restart(self):
        try:
            print("Restarting HiveMQ server...")
            self.java_execution_completed.clear()
            if self.is_running:
                self.mqtt_instance.stopServer()
            self.mqtt_instance.startServer()
            print("HiveMQ server restarted.")
            self.java_execution_completed.set()
        except Exception as e:
            print("Error:", e)
            self.java_execution_completed.set()

    def is_running(self):
        try:
            return self.mqtt_instance.isServerRunning()
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    mqtt_manager = MQTTBrokerManager()
    mqtt_manager.start()

    # Wait for some time (for demonstration purposes)
    time.sleep(10)

    # Stop the MQTT broker
    mqtt_manager.stop()
