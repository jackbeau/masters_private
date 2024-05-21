from gui.app import App
from async_tkinter_loop import async_handler, async_mainloop
# from server_backend import ServerBackend

if __name__ == "__main__":

    # Start MQTT broker
    # start_mqtt_broker()

    # Initialize server backend
    # server_backend = ServerBackend()

    # Start Tkinter UI
    # app = App(server_backend)
    app = App()
    
    async_mainloop(app)

    # If the app is closed, stop the MQTT broker
    quit()
