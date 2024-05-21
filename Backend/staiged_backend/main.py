from gui.app import App
from mqtt_broker import MQTTBrokerManager
from async_tkinter_loop import async_handler, async_mainloop
# from server_backend import ServerBackend

if __name__ == "__main__":

    # Start MQTT broker
    # start_mqtt_broker()

    # Initialize server backend
    # server_backend = ServerBackend()

    # Start Tkinter UI
    # app = App(server_backend)
    
    # mqtt_manager = MQTTBrokerManager()
    # mqtt_manager.start()

    app = App()
    print("ok")
    async_mainloop(app)
    print("hi")
    # mqtt_manager.stop()
    quit()
    exit(0)