import asyncio
from paho.mqtt import client as mqtt_client
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes 
import logging
import time
import json

# TODO
# CLean start bug
# Move to urils and make control page sync

logging.basicConfig(level=logging.INFO)

class MQTTClient:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.subscriptions = {}
        self.messages = []

        self.client = mqtt_client.Client(client_id=self.client_id, reconnect_on_failure=True, protocol=mqtt_client.MQTTv5, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    def connect(self):
        properties = Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval = 3600  #set session expiry interval
        while True:
            try:
                self.client.connect(self.broker, self.port, clean_start=False, properties=properties)
                logging.info("Connected to MQTT broker")
                for topic, callback in self.subscriptions.items():
                    self.client.subscribe(topic, qos=2)
                break  # Exit the loop if connection is successful
            except ConnectionRefusedError:
                logging.info("Connection refused. Retrying in 5 seconds...")
                time.sleep(5)
                continue  # Retry connection

    def on_connect(self, client, userdata, flags, reasonCode,properties=None):
        print('Connected ',flags)

    def on_disconnect(self, client, userdata, disconnect_flags, rc, properties=None):
        print('Received Disconnect ',rc)

    def on_subscribe(self, client, userdata, mid, granted_qos,properties=None):
        print('SUBSCRIBED')
    
    def publish(self, topic, message, retain=False):
        logging.info(f"Publishing {message} to {topic}")
        self.client.publish(topic, message, qos=2, retain=retain)

    def subscribe(self, topic, callback):
        self.client.subscribe(topic, qos=2)
        self.subscriptions[topic] = callback

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)
        if topic in self.subscriptions:
            del self.subscriptions[topic]

    def on_message(self, client, userdata, message):

        msg=str(message.payload.decode("utf-8"))
        self.messages.append(msg)
        print('RECV Topic = ',message.topic)
        print('RECV MSG =', msg)

def main():
    broker = '0.0.0.0'
    port = 1883
    client_id = "server"
    
    mqtt_client = MQTTClient(broker, port, client_id)
    mqtt_client.connect()

    # Example subscribing to a topic with a callback
    def handle_message(topic, payload):
        print(f"Received `{payload}` from `{topic}` topic")
    mqtt_client.subscribe("test", handle_message)

    # Example publishing a message
    mqtt_client.publish("local_server/racker/position", "Hello, MQTT!")
    mqtt_client.client.loop_forever()


if __name__ == '__main__':
    main()
