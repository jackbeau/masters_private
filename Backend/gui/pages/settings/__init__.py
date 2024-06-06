"""
Author: Jack Beaumont
Date: 06/06/2024

This module provides a GUI for managing various settings, including general
settings, microphone settings, camera settings, and stage zone settings.

Classes:
    MenuDataItem: Represents an item in the settings menu.
    SettingsPage: The main settings page frame containing the sidebar and page
                  container.
    SideBar: The sidebar frame containing menu items for navigating settings.
    MenuItem: A widget representing an individual item in the sidebar.
    PageContainer: A container for displaying the content of the selected
                   settings page.
    ImageLoader: A utility class for loading and caching images.
"""

from PIL import Image, ImageTk
from tkinter import Frame, StringVar, Label
from tkinter import ttk
import customtkinter
import logging

from gui.pages.settings.microphone_page import MicrophonePage
from gui.pages.settings.camera_page import CameraPage
from gui.pages.settings.stage_zones_page import StageZonesPage
from gui.core.constants.styles import colours, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MenuDataItem:
    """
    Represents an item in the settings menu.

    Attributes:
        title (str): The title of the menu item.
        image_path (str): The file path to the menu item's image.
        child (class): The class representing the settings page to navigate to.
    """

    def __init__(self, title, image_path, child):
        self.title = title
        self.image_path = image_path
        self.child = child


class SettingsPage(Frame):
    """
    The main settings page frame containing the sidebar and page container.

    Attributes:
        controller: The controller object for managing page transitions.
        menu_items (list): List of MenuDataItem objects representing the menu
        items.
        current_page (MenuDataItem): The currently selected menu item.
    """

    NAME = "Settings"

    def __init__(self, controller, parent, *args, **kwargs):
        super().__init__(
            parent, *args, **kwargs, background=colours.off_black_80
        )
        self.controller = controller

        # Define the menu items
        self.menu_items = [
            MenuDataItem(
                title="General",
                image_path="gui/assets/settings_icon.png",
                child="general",
            ),
            MenuDataItem(
                title="Microphone",
                image_path="gui/assets/microphone_icon.png",
                child=MicrophonePage,
            ),
            MenuDataItem(
                title="Camera",
                image_path="gui/assets/camera_icon.png",
                child=CameraPage,
            ),
            MenuDataItem(
                title="Stage Zones",
                image_path="gui/assets/stage_zones_icon.png",
                child=StageZonesPage,
            ),
        ]

        self.current_page = self.menu_items[2]
        self.render()

    def close(self):
        """
        Closes the settings page.
        """
        logger.info("Closing settings page.")
        self.controller.toggle_settings()
        self.page_container.close()

    def render(self):
        """
        Renders the settings page, including the sidebar and the page
        container.
        """
        self.rowconfigure(0, minsize=300, weight=1)
        self.columnconfigure(1, minsize=300, weight=1)

        self.sidebar = SideBar(
            self,
            self.menu_items,
            self.navigate,
            self.current_page,
            padx=10,
            pady=14,
            bg=colours.off_black_100,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.page_container = PageContainer(
            self, self.current_page.child, bg=colours.off_black_80, padx=18
        )
        self.page_container.grid(row=0, column=1, sticky="nsew", pady=(14, 8))

        self.page_container.current_page_str.set(
            self.NAME + " > " + self.current_page.child.NAME
        )

    def navigate(self, target_page):
        """
        Navigates to the target page.

        Args:
            target_page (MenuDataItem): The target page to navigate to.
        """
        logger.info(f"Navigating to {target_page.title}.")
        self.page_container.destroy()
        self.page_container.close()
        self.current_page = target_page
        self.page_container = PageContainer(
            self, self.current_page.child, bg=colours.off_black_80, padx=18
        )
        self.page_container.grid(row=0, column=1, sticky="nsew", pady=(14, 8))
        self.page_container.current_page_str.set(
            self.NAME + " > " + self.current_page.child.NAME
        )
        self.sidebar.update_menu(self.current_page)


class SideBar(Frame):
    """
    The sidebar frame containing menu items for navigating settings.

    Attributes:
        current_page (MenuDataItem): The currently selected menu item.
        menu_items (list): List of MenuDataItem objects representing the menu
                           items.
        navigator (function): The function to call when a menu item is
                              selected.
    """

    def __init__(
        self, parent, menu_items, navigator, current_page, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.current_page = current_page
        self.menu_items = menu_items
        self.navigator = navigator
        self.render()

    def render_items(self, parent):
        """
        Renders the menu items in the sidebar.

        Args:
            parent (tkinter.Widget): The parent widget to attach the items to.
        """
        for menu_item in self.menu_items:
            highlight = True if self.current_page == menu_item else None
            menu_item_widget = MenuItem(
                parent,
                self.navigator,
                menu_item,
                highlight,
                fg_color=(
                    colours.user_accent if highlight else colours.off_black_100
                ),
            )
            menu_item_widget.pack(fill="x", pady=(0, 0))

    def render(self):
        """
        Renders the sidebar, including the settings title and menu items.
        """
        lbl_settings = text(self, text="Settings", style="SideBarHeading")
        lbl_settings.pack(pady=(0, 10), padx=(4, 60))

        self.frm_menu = Frame(self, background=colours.off_black_100)
        self.frm_menu.pack(anchor="w", fill="x")

        self.render_items(self.frm_menu)

    def update_menu(self, target_page):
        """
        Updates the sidebar menu to highlight the selected page.

        Args:
            target_page (MenuDataItem): The selected menu item.
        """
        self.current_page = target_page
        for widget in self.frm_menu.winfo_children():
            widget.destroy()
        self.render_items(self.frm_menu)


class MenuItem(customtkinter.CTkFrame):
    """
    A widget representing an individual item in the sidebar.

    Attributes:
        IMAGE_SIZE (tuple): The size of the menu item image.
    """

    IMAGE_SIZE = (24, 24)

    def __init__(
        self, parent, navigate, menu_item, highlight=False, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.navigate = navigate
        self.create_item(menu_item, highlight)

    def create_item(self, menu_item, highlight):
        """
        Creates the menu item widget.

        Args:
            menu_item (MenuDataItem): The menu item data.
            highlight (bool): Whether the item should be highlighted.
        """
        bg_color = colours.user_accent if highlight else colours.off_black_100

        img = customtkinter.CTkImage(
            light_image=Image.open(menu_item.image_path),
            dark_image=Image.open(menu_item.image_path),
            size=self.IMAGE_SIZE,
        )

        lbl_menu_item_img = customtkinter.CTkLabel(self, image=img, text="")
        lbl_menu_item_img.pack(fill="y", side="left", padx=(4, 4), pady=4)

        lbl_menu_item = Label(
            self,
            text=menu_item.title,
            bg=bg_color,
            font=(".AppleSystemUIFont", 12),
        )
        lbl_menu_item.pack(fill="y", side="left")

        if not highlight:
            self.bind(
                "<Button-1>", lambda event, page=menu_item: self.navigate(page)
            )
            lbl_menu_item_img.bind(
                "<Button-1>", lambda event, page=menu_item: self.navigate(page)
            )
            lbl_menu_item.bind(
                "<Button-1>", lambda event, page=menu_item: self.navigate(page)
            )


class PageContainer(Frame):
    """
    A container for displaying the content of the selected settings page.

    Attributes:
        current_page_str (StringVar): The string variable for the current page
                                      path.
    """

    def __init__(self, parent, page_class, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pages = {}
        self.current_page_str = StringVar(value="")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.render(parent, page_class)

    def create_top_bar(self, parent):
        """
        Creates the top bar with the current page path and close button.

        Args:
            parent (tkinter.Widget): The parent widget.
        """
        frm_topbar = Frame(self, bg=colours.off_black_80)
        frm_topbar.pack(anchor="w", fill="x")

        lbl_path = Label(
            frm_topbar,
            textvariable=self.current_page_str,
            bg=colours.off_black_80,
            font=(".AppleSystemUIFont", 12, "bold"),
        )
        lbl_path.pack(side="left")

        btn_close = ttk.Button(frm_topbar, text="Close", command=parent.close)
        btn_close.pack(side="right")

    def close(self):
        """
        Closes the current page.
        """
        self.page.close()

    def render(self, parent, page_class):
        """
        Renders the page container.

        Args:
            parent (tkinter.Widget): The parent widget.
            page_class (class): The class representing the page to display.
        """
        self.create_top_bar(parent)

        self.container = Frame(self, bg=colours.off_black_80)
        self.container.pack(side="top", fill="both", expand=True)

        self.page = page_class(
            self.container, background=colours.off_black_80, pady=12
        )
        self.page.grid(row=0, column=0, sticky="nsew")


class ImageLoader:
    """
    A utility class for loading and caching images.

    Attributes:
        loaded_images (dict): A dictionary caching loaded images.
    """

    def __init__(self):
        self.loaded_images = {}

    def load_image(self, image_path, size):
        """
        Loads an image from the specified path and resizes it.

        Args:
            image_path (str): The path to the image file.
            size (tuple): The desired size of the image.

        Returns:
            PhotoImage: The loaded and resized image.
        """
        if image_path not in self.loaded_images:
            img = Image.open(image_path)
            img = img.resize(size, resample=Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.loaded_images[image_path] = img
        return self.loaded_images[image_path]
