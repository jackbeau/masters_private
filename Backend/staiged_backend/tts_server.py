from backend.speech_to_line import SpeechToLine
from backend.mqtt_controller.mqtt_controller import MQTTController
import threading


def start_speech_to_line_async():
    thread = threading.Thread(target=speech_to_line.start)
    thread.start()


broker = '0.0.0.0'
port = 1883
client_id = "server"

mqtt_controller = MQTTController(broker, port, client_id)
mqtt_controller.connect()

speech_to_line = SpeechToLine(mqtt_controller=mqtt_controller)

# Example subscribing to a topic with a callback
def handle_message(topic, payload):
    if topic == "local_server/tracker/cmd":
        if payload == "start":
            # Start the SpeechToLine service
            print("starting")
            start_speech_to_line_async()
        elif payload == "stop":
            # Stop the SpeechToLine service
            print("stopping")
            speech_to_line.stop = True
            
    else:
        print(f"Received `{payload}` from `{topic}` topic")

mqtt_controller.subscribe("local_server/tracker/cmd", handle_message)

# Example publishing a message
mqtt_controller.publish("local_server/tracker/position", "Hello, MQTT!")

mqtt_controller.client.loop_forever()
