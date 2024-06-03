import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from gui.pages.settings import SettingsPage
from gui.pages.home import HomePage
from gui.core.constants.styles import colours, configure_styles
import logging
import customtkinter


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # self.server_backend = server_backend
        
        # if 'win' in sys.platform:
    #     ctypes.windll.shcore.SetProcessDpiAwareness(1)

        ico = Image.open('gui/assets/icon.png')
        photo = ImageTk.PhotoImage(ico)

        self.minsize(800, 700)
        self.title("Stage Assistant")
        self.wm_iconphoto(False, photo)
        self.eval('tk::PlaceWindow . center')

        self.show_settings = False

        self.page_container = tk.Frame(self)
        self.page_container.pack(expand=True, fill="both")
        self.page_container.grid_columnconfigure(0, weight=1, uniform=True)
        self.page_container.grid_rowconfigure(0, weight=1, uniform=True)

        self.home_page = HomePage(self, self.page_container)
        self.home_page.grid(row=0, column=0, sticky="nsew")

        configure_styles(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_settings(self):
        logging.info("Toggling settings")
        self.show_settings = not self.show_settings
        if self.show_settings is True:
            self.settings_page = SettingsPage(self, self.page_container)
            self.settings_page.grid(row=0, column=0, sticky="nsew")
            self.settings_page.tkraise()
        else:
            self.settings_page.destroy()
            self.home_page.load_settings()
            self.home_page.grid(row=0, column=0, sticky="nsew")
            self.home_page.tkraise()

    def on_closing(self):
        print("closing")
        if self.show_settings is True:
            self.settings_page.page_container.close()
        else:
            self.home_page.mqtt_manager.stop()
        self.destroy()
        self.quit()
        quit()