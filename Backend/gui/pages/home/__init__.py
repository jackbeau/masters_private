from PIL import Image, ImageTk
from tkinter import Frame, StringVar, Label
import os
import sys
from tkinter import ttk
import customtkinter
import logging
import requests
from broker import MQTTBrokerManager
from gui.pages.shared.settings_manager import SettingsManager
from async_tkinter_loop import async_handler, async_mainloop
import asyncio
import datetime
from gui.pages.shared.video_utils import get_video_devices
import grpc

# Ensure the module path is correctly set
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../server/grpc/python/server')))

import service_pb2
import service_pb2_grpc

from gui.core.constants.styles import colours, text

class HomePage(Frame):
    NAME = "Home"

    def __init__(self, controller, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs, background=colours.off_black_100)
        self.loop = asyncio.get_event_loop()
        
        self.mqtt_manager = MQTTBrokerManager()
        self.controller = controller

        self.settings_manager = SettingsManager()

        self.label_vars = {}
        
        self.status_info = {
            "MQTT Server": "",
            "RPC Server": "n/a",
            "API Server": "n/a",
            "Speech-to-line": "n/a",
            "Performer Tracker": "n/a",
            "Camera": "",
            "Microphone": "",
            "IP": os.environ['HIVEMQ_IP'],
            "Server Port": os.environ['HIVEMQ_PORT'],
            "Connected Devices": "0",
            "Software Version": "Beta"
        }

        self.update_system_info("MQTT Server", "Starting")
        self.render()
        self.load_settings()
        self.start_server()
        self.loop.create_task(self.update_status_periodically())

    @async_handler
    async def start_server(self):
        self.update_system_info("MQTT Server", "Starting")
        await self.loop.run_in_executor(None, self.mqtt_manager.start)
        self.update_system_info("MQTT Server", "Running")
        self.status_overview()

    @async_handler
    async def restart_server(self):
        self.update_system_info("MQTT Server", "Restarting")
        self.status_overview()
        await self.loop.run_in_executor(None, self.mqtt_manager.restart)
        self.update_system_info("MQTT Server", "Running")
        self.status_overview()

    @async_handler
    async def stop_server(self):
        self.update_system_info("MQTT Server", "Stopping")
        self.status_overview()
        await self.loop.run_in_executor(None, self.mqtt_manager.stop)
        self.update_system_info("MQTT Server", "Stopped")
        self.status_overview()

    def load_settings(self):
        settings = self.settings_manager.load_settings()
        
        self.update_system_info(
            "Microphone",
            settings.get("microphone", {}).get("microphone_device", "")
        )
        video_devices = get_video_devices()
        video_device = next((device for device in video_devices if device["uniqueID"] == settings.get("camera", {}).get("video_device_id", "")), None)

        if video_device is not None:
            self.update_system_info(
                "Camera",
                video_device["localizedName"]
                
            )
        else:
            self.update_system_info(
                "Camera",
                ""
                
            )      
        print("Reloaded settings")

    def update_system_info(self, key, new_value):
        if key in self.label_vars:
            self.label_vars[key].set(new_value)
        else:
            print("Key not found.")

    def gen_system_info(self, parent):
        frm_parameters = Frame(parent, background=colours.off_black_100)
        frm_parameters.pack(expand=True, fill="y", side="left")

        frm_values = Frame(parent, background=colours.off_black_100)
        frm_values.pack(expand=True, fill="y", side="left")

        def lbl_key(text):
            lbl_param = Label(
                frm_parameters, text=text, font=(".AppleSystemUIFont", 12), background=colours.off_black_100, anchor="w"
            )
            lbl_param.pack(expand=True, fill="x", pady=4)

        def lbl_val(text):
            lbl_val = Label(
                frm_values, textvariable=text, font=(".AppleSystemUIFont", 12), background=colours.off_black_100, anchor="w"
            )
            lbl_val.pack(expand=True, fill="x", pady=4)

        for key, value in self.status_info.items():
            var = StringVar()
            var.set(value) 
            self.label_vars[key] = var

            lbl_key(key)
            lbl_val(var)

    def status_overview(self):
        if hasattr(self, 'frm_col_0_centre'):
            self.frm_col_0_centre.destroy()
        self.frm_col_0_centre = Frame(self.frm_col_0, background=colours.off_black_100)
        self.frm_col_0_centre.place(relx=.5, rely=.5, anchor="c")

        if self.mqtt_manager.is_running():
            img = customtkinter.CTkImage(light_image=Image.open("gui/assets/running.png"), size=(64, 64))
            lbl_status_img = customtkinter.CTkLabel(self.frm_col_0_centre, image=img, text="")
            lbl_status_img.pack()
            
            lbl_status = Label(
                self.frm_col_0_centre, text="Up and running", font=(".AppleSystemUIFont", 16, "bold"), background=colours.off_black_100
            )
            lbl_status.pack()

            lbl_restart_time = Label(
                self.frm_col_0_centre, text=f'Last checked: {datetime.datetime.now()}', font=(".AppleSystemUIFont", 12), background=colours.off_black_100
            )
            lbl_restart_time.pack()
        else:
            img = customtkinter.CTkImage(light_image=Image.open("gui/assets/stopped.png"), size=(64, 64))
            lbl_status_img = customtkinter.CTkLabel(self.frm_col_0_centre, image=img, text="")
            lbl_status_img.pack()
            
            lbl_status = Label(
                self.frm_col_0_centre, text="Stopped", font=(".AppleSystemUIFont", 16, "bold"), background=colours.off_black_100
            )
            lbl_status.pack()

            lbl_restart_time = Label(
                self.frm_col_0_centre, text=f'Last checked: {datetime.datetime.now()}', font=(".AppleSystemUIFont", 12), background=colours.off_black_100
            )
            lbl_restart_time.pack()

    async def update_status_periodically(self):  # Change this to be an async function
        while True:
            await asyncio.sleep(5)
            try:
                response = requests.get('http://localhost:4000/status')
                if response.status_code == 200 and response.json().get('status') == 'running':
                    self.update_system_info("API Server", "Running")
                else:
                    self.update_system_info("API Server", "Stopped")
            except requests.ConnectionError:
                self.update_system_info("API Server", "Stopped")
            
            try:
                with grpc.insecure_channel('localhost:50051') as channel:
                    stub = service_pb2_grpc.ScriptServiceStub(channel)
                    response = stub.GetStatuses(service_pb2.StatusRequest())
                    self.update_system_info("RPC Server", response.rpc_status)
                    self.update_system_info("Speech-to-line", response.speech_to_line_status)
                    self.update_system_info("Performer Tracker", response.performer_tracker_status)         
            except grpc.RpcError:
                self.update_system_info("RPC Server", "Stopped")
                self.update_system_info("Transcription Algorithm", "Stopped")

            self.status_overview()

    def render(self):
        frm_topbar = Frame(self, bg=colours.off_black_100)
        frm_topbar.pack(anchor="n", fill="x", padx=10, pady=14)

        lbl_path = text(
            frm_topbar, text="Stage Assistant Server", style="SideBarHeading"
        )
        lbl_path.pack(side="left", pady=(0, 10), padx=(4, 60))

        btn_settings = ttk.Button(
            frm_topbar, text="Settings",
            command=self.controller.toggle_settings
        )
        btn_settings.pack(side="right", padx=4)
        
        btn_stop = ttk.Button(
            frm_topbar, text="Stop", command=self.stop_server
        )
        btn_stop.pack(side="right", padx=4)

        btn_restart = ttk.Button(
            frm_topbar, text="Restart", command=self.restart_server
        )
        btn_restart.pack(side="right", padx=4)

        frm_body = Frame(self, background=colours.off_black_100)
        frm_body.pack(fill="both", expand=True, anchor="n")

        frm_body.grid_columnconfigure((0,1), weight=1, uniform=True)
        frm_body.grid_rowconfigure(0, weight=1, uniform=True)

        self.frm_col_0 = Frame(frm_body, background=colours.off_black_100)
        self.frm_col_0.grid(row=0, column=0, sticky="nsew")

        self.status_overview()

        frm_col_1 = Frame(frm_body, background=colours.off_black_100)
        frm_col_1.grid(row=0, column=1, sticky="nsew") 

        self.frm_col_1_centre = Frame(frm_col_1, background=colours.off_black_100)
        self.frm_col_1_centre.place(relx=.5, rely=.5, anchor="c")

        self.gen_system_info(self.frm_col_1_centre)
