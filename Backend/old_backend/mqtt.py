import random
import time
from paho.mqtt import client as mqtt_client


class MQTTHandler:
    def __init__(self, client_id_prefix):
        self.broker = 'broker'
        self.port = 1883
        self.topic = "python/mqtt"
        self.client_id = f'{client_id_prefix}-{random.randint(0, 1000)}'
        # self.username = 'emqx'
        # self.password = 'public'
        self.client = self.connect_mqtt()

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        # client.username_pw_set(self.username, self.password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def subscribe(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        self.client.subscribe(self.topic)
        self.client.on_message = on_message

    def publish(self):
        msg_count = 1
        while True:
            time.sleep(1)
            msg = f"messages: {msg_count}"
            result = self.client.publish(self.topic, msg)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{msg}` to topic `{self.topic}`")
            else:
                print(f"Failed to send message to topic {self.topic}")
            msg_count += 1
            if msg_count > 5:
                break

    def run(self):
        self.client.loop_start()
        self.publish()
        self.subscribe()
        self.client.loop_forever()


if __name__ == '__main__':
    mqtt_handler = MQTTHandler(client_id_prefix="mqtt")
    mqtt_handler.run()
