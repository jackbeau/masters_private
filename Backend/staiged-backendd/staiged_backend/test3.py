import paho.mqtt.client as mqtt

# Define callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, mid):
    print("Message published")

# Create an MQTT client instance
client = mqtt.Client()

# Assign callback functions
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the MQTT broker (replace "localhost" with your broker's IP if it's different)
client.connect("localhost", 1883, 60)

# Publish a message to a topic
client.publish("test/topic", "Hello, MQTT!")

# Loop to keep the client network loop running
client.loop_forever()
