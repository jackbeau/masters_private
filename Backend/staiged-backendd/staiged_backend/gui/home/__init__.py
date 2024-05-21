from PIL import Image, ImageTk
from tkinter import Frame, StringVar, Label
from tkinter import ttk
import customtkinter
import logging
from mqtt_broker import MQTTBrokerManager
from utils import SettingsManager
from async_tkinter_loop import async_handler, async_mainloop
import asyncio
import os
import datetime

from gui.styles import colours, text


# class MenuDataItem:
#     def __init__(self, title, image_path, child):
#         self.title = title
#         self.image_path = image_path
#         self.child = child

class HomePage(Frame):
    NAME = "Home"

    def __init__(self, controller, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs,
                       background=colours.off_black_100)
        self.loop = asyncio.get_event_loop()
        
        self.mqtt_manager = MQTTBrokerManager()
        self.controller = controller

        self.settings_manager = SettingsManager()

        self.label_vars = {}
        
        self.status_info = {
            "MQTT Server": "",
            "Backend": "n/a",
            "Camera": "",
            "Microphone": "",
            "IP": os.environ['HIVEMQ_IP'],
            "Server Port": os.environ['HIVEMQ_PORT'],
            "Connected Devices": "0",
            "Software Version": "Beta"
        }

        # self.current_page = self.menu_items[2]

        self.update_system_info("MQTT Server", "Starting")
        self.render()
        self.load_settings()
        # self.start_server()

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
        print("rr")
        self.update_system_info(
            "Microphone",
            settings.get("microphone", {}).get("microphone_device", "")
        )
        self.update_system_info(
            "Camera",
            settings.get("camera", {}).get("video_device", "")
        )
        print("jjkkj")

        # settings.get()
    
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

        print(self.mqtt_manager.is_running())
        if self.mqtt_manager.is_running():
            img = customtkinter.CTkImage(light_image=Image.open("gui/resources/running.png"),
                                  size = (64, 64))
            
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
            img = customtkinter.CTkImage(light_image=Image.open("gui/resources/Stopped.png"),
                                  size = (64, 64))
            
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

        frm_col_1_centre = Frame(frm_col_1, background=colours.off_black_100)
        frm_col_1_centre.place(relx=.5, rely=.5, anchor="c")

        self.gen_system_info(frm_col_1_centre)

        # self.page_container = PageContainer(self, self.current_page.child, bg=colours.off_black_80, padx=18)
        # self.page_container.grid(row=0, column=1, sticky="nsew", pady=(14, 8))

        # self.page_container.current_page_str.set(self.NAME + " > " + self.current_page.child.NAME)

    # def navigate(self, target_page):
    #     logging.info("Navigating to", target_page)
    #     self.current_page = target_page
    #     self.page_container.destroy()
    #     self.page_container = PageContainer(self, self.current_page.child, bg=colours.off_black_80, padx=18)
    #     self.page_container.grid(row=0, column=1, sticky="nsew", pady=(14, 8))
    #     self.page_container.current_page_str.set(self.NAME + " > " + self.current_page.child.NAME)
    #     self.sidebar.update_menu(self.current_page)

# class PageContainer(Frame):
#     def __init__(self, parent, page_class, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.pages = {}
#         self.current_page_str = StringVar(value="")
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(0, weight=1)

#         self.render(parent, page_class)



#     def render(self, parent, page_class):
#         # top  bar
#         self.create_top_bar(parent)

#         # creating a container
#         self.container = Frame(self, bg=colours.off_black_80)
#         self.container.pack(side="top", fill="both", expand=True)

#         # self.container.grid_rowconfigure(0, weight=1)
#         # self.container.grid_columnconfigure(0, weight=1)

#         self.page = page_class(
#             self.container, background=colours.off_black_80, pady=12)

#         self.page.grid(row=0, column=0, sticky="nsew")


# class ImageLoader:
#     def __init__(self):
#         self.loaded_images = {}

#     def load_image(self, image_path, size):
#         if image_path not in self.loaded_images:
#             img = Image.open(image_path)
#             img = img.resize(size, resample=Image.LANCZOS)
#             img = ImageTk.PhotoImage(img)
#             self.loaded_images[image_path] = img
#         return self.loaded_images[image_path]
    