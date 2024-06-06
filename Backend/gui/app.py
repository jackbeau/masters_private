"""
Author: Jack Beaumont
Date: 06/06/2024

This module defines the main application class for the Stage Assistant
application using the tkinter framework.
"""

import tkinter as tk
from PIL import Image, ImageTk
from gui.pages.settings import SettingsPage
from gui.pages.home import HomePage
from gui.core.constants.styles import configure_styles
import logging
import customtkinter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class App(customtkinter.CTk):
    def __init__(self):
        """
        Initializes the main application window, sets up the home page and
        styles.
        """
        super().__init__()

        # Load and set the application icon
        ico = Image.open("gui/assets/icon.png")
        photo = ImageTk.PhotoImage(ico)
        self.wm_iconphoto(False, photo)

        # Set the minimum window size and title
        self.minsize(800, 700)
        self.title("Stage Assistant")

        # Center the window on the screen
        self.eval("tk::PlaceWindow . center")

        self.show_settings = False

        # Create the main page container frame
        self.page_container = tk.Frame(self)
        self.page_container.pack(expand=True, fill="both")
        self.page_container.grid_columnconfigure(0, weight=1, uniform=True)
        self.page_container.grid_rowconfigure(0, weight=1, uniform=True)

        # Initialize the home page
        self.home_page = HomePage(self, self.page_container)
        self.home_page.grid(row=0, column=0, sticky="nsew")

        # Apply styles
        configure_styles(self)

        # Set the close window protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_settings(self):
        """
        Toggles the visibility of the settings page.
        """
        logging.info("Toggling settings")
        self.show_settings = not self.show_settings

        if self.show_settings:
            self.settings_page = SettingsPage(self, self.page_container)
            self.settings_page.grid(row=0, column=0, sticky="nsew")
            self.settings_page.tkraise()
        else:
            self.settings_page.destroy()
            self.home_page.load_settings()
            self.home_page.grid(row=0, column=0, sticky="nsew")
            self.home_page.tkraise()

    def on_closing(self):
        """
        Handles the application close event.
        """
        logging.info("Application is closing")

        if self.show_settings:
            self.settings_page.page_container.close()
        else:
            self.home_page.mqtt_manager.stop()

        self.destroy()
        self.quit()


# Entry point for the application
if __name__ == "__main__":
    app = App()
    app.mainloop()
