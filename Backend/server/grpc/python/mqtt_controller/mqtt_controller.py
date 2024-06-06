"""
Author: Jack Beaumont
Date: 06/06/2024
Description: MQTT Controller module for handling MQTT connections,
subscriptions, and publishing messages.
"""

import logging
import time
import json
from paho.mqtt import client as mqtt_client
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

logging.basicConfig(level=logging.INFO)


class MQTTController:
    def __init__(self, broker: str, port: int, client_id: str):
        """
        Initialize the MQTTController instance.

        :param broker: MQTT broker address
        :param port: MQTT broker port
        :param client_id: Client ID for the MQTT connection
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.subscriptions = {}

        self.client = mqtt_client.Client(
            client_id=self.client_id,
            reconnect_on_failure=True,
            protocol=mqtt_client.MQTTv5,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    def connect(self):
        """
        Connect to the MQTT broker and start the network loop.
        """
        properties = Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval = 3600  # set session expiry interval
        while True:
            try:
                self.client.connect(
                    self.broker,
                    self.port,
                    clean_start=False,
                    properties=properties,
                )
                self.client.loop_start()  # Start the loop to process network
                logging.info("Connected to MQTT broker")
                for topic, callback in self.subscriptions.items():
                    self.client.subscribe(topic, qos=2)
                break  # Exit the loop if connection is successful
            except ConnectionRefusedError:
                logging.warning("Connection refused. Retrying in 5 seconds...")
                time.sleep(5)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback when the client connects to the MQTT broker.

        :param client: The client instance
        :param userdata: The private user data as set in Client() or
                         userdata_set()
        :param flags: Response flags sent by the broker
        :param rc: The connection result
        :param properties: The properties associated with the connection
                           (optional)
        """
        if rc == 0:
            logging.info("Connected to MQTT broker")
            for topic, callback in self.subscriptions.items():
                self.client.subscribe(topic, qos=2)
        else:
            logging.warning(f"Failed to connect, return code {rc}")

    def on_disconnect(
        self, client, userdata, disconnect_flags, reason_code, properties=None
    ):
        """
        Callback when the client disconnects from the MQTT broker.

        :param client: The client instance
        :param userdata: The private user data as set in Client() or
                         userdata_set()
        :param disconnect_flags: Response flags sent by the broker
        :param reason_code: The reason code for disconnection
        :param properties: The properties associated with the disconnection
                           (optional)
        """
        logging.warning(
            f"Disconnected from MQTT broker with reason code {reason_code}"
        )

    def on_subscribe(
        self, client, userdata, mid, granted_qos, properties=None
    ):
        """
        Callback when the client subscribes to a topic.

        :param client: The client instance
        :param userdata: The private user data as set in Client() or
                         userdata_set()
        :param mid: The message ID for the subscribe request
        :param granted_qos: The granted QoS level for the subscription
        :param properties: The properties associated with the subscription
                           (optional)
        """
        logging.info(f"Subscribed with mid {mid}, granted QoS {granted_qos}")

    def publish(self, topic: str, message: str, retain: bool = False):
        """
        Publish a message to a topic.

        :param topic: The topic to publish to
        :param message: The message to publish
        :param retain: Retain the message on the broker (default is False)
        """
        logging.info(f"Publishing {message} to {topic}")
        result = self.client.publish(topic, message, qos=0, retain=retain)
        status = result.rc
        if status == mqtt_client.MQTT_ERR_SUCCESS:
            logging.info(f"Message published successfully to {topic}")
        else:
            logging.warning(
                f"Failed to publish message to {topic}: "
                f"{mqtt_client.error_string(status)}"
            )

    def subscribe(self, topic: str, callback):
        """
        Subscribe to a topic.

        :param topic: The topic to subscribe to
        :param callback: The callback function to handle messages from the
                         topic
        """
        self.client.subscribe(topic, qos=2)
        self.subscriptions[topic] = callback

    def unsubscribe(self, topic: str):
        """
        Unsubscribe from a topic.

        :param topic: The topic to unsubscribe from
        """
        self.client.unsubscribe(topic)
        if topic in self.subscriptions:
            del self.subscriptions[topic]

    def on_message(self, client, userdata, msg):
        """
        Callback when a message is received from a subscribed topic.

        :param client: The client instance
        :param userdata: The private user data as set in Client() or
                         userdata_set()
        :param msg: The received message instance
        """
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
        """
        Disconnect from the MQTT broker and stop the network loop.
        """
        logging.info("Disconnecting from MQTT broker...")
        self.client.loop_stop()  # Stop the loop
        self.client.disconnect()
