import logging
import time
import json
from paho.mqtt import client as mqtt_client
from paho.mqtt.properties import Properties 
from paho.mqtt.packettypes import PacketTypes

logging.basicConfig(level=logging.INFO)

class MQTTController:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.subscriptions = {}

        self.client = mqtt_client.Client(client_id=self.client_id, reconnect_on_failure=True, protocol=mqtt_client.MQTTv5, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    def connect(self):
        properties = Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval = 3600  # set session expiry interval
        while True:
            try:
                self.client.connect(self.broker, self.port, clean_start=False, properties=properties)
                self.client.loop_start()  # Start the loop to process network traffic and reconnect if needed
                logging.info("Connected to MQTT broker")
                for topic, callback in self.subscriptions.items():
                    self.client.subscribe(topic, qos=2)
                break  # Exit the loop if connection is successful
            except ConnectionRefusedError:
                logging.info("Connection refused. Retrying in 5 seconds...")
                time.sleep(5)
                continue  # Retry connection

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            for topic, callback in self.subscriptions.items():
                self.client.subscribe(topic, qos=2)
        else:
            logging.info(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties=None):
        logging.warning(f"Disconnected from MQTT broker with reason code {reason_code}")

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        logging.info(f"Subscribed with mid {mid}, granted QoS {granted_qos}")

    def publish(self, topic, message, retain=False):
        logging.info(f"Publishing {message} to {topic}")
        result = self.client.publish(topic, message, qos=0, retain=retain)
        status = result.rc
        if status == mqtt_client.MQTT_ERR_SUCCESS:
            logging.info(f"Message published successfully to {topic}")
        else:
            logging.warning(f"Failed to publish message to {topic}: {mqtt_client.error_string(status)}")

    def subscribe(self, topic, callback):
        self.client.subscribe(topic, qos=2)
        self.subscriptions[topic] = callback

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)
        if topic in self.subscriptions:
            del self.subscriptions[topic]

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        if topic in self.subscriptions:
            callback = self.subscriptions[topic]
            if callback:
                payload = msg.payload.decode()
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    pass
                callback(topic, payload)

    def disconnect(self):
        logging.info("Disconnecting from MQTT broker...")
        self.client.loop_stop()  # Stop the loop
        self.client.disconnect()
