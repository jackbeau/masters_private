"""
Author: Jack Beaumont
Date: 06/06/2024

This module defines the GUI theme and styling for a Tkinter application,
including color schemes, font settings, and custom label configurations.

Classes:
    Colours: Defines a set of color constants used throughout the GUI.
    Fonts: Defines font settings for different types of text elements.

Functions:
    text(parent, text, style, *args, **kwargs): Creates a Tkinter label with
                                                the specified text and style.
    configure_styles(root): Configures the styles for various Tkinter widgets.

"""

import tkinter as tk
from tkinter import ttk
from gui.core.theme.sv_ttk import set_theme
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Colours:
    white = "#FFFFFF"
    off_black_100 = "#151515"
    off_black_80 = "#252525"
    off_black_60 = "#343434"
    user_accent = "#0A7AFF"


colours = Colours()


class Fonts:
    class Heading1:
        font = "inter"
        size = "18"
        width = "bold"

    class Heading2:
        font = "inter"
        size = "12"
        width = "bold"

    class Label:
        font = "inter"
        size = "12"
        width = "regular"

    class Text:
        font = "inter"
        size = "12"
        width = "regular"


fonts = Fonts()


def text(parent, text, style, *args, **kwargs):
    """
    Creates a Tkinter label with the specified text and style.

    Parameters:
        parent (tk.Widget): The parent widget for the label.
        text (str): The text to be displayed in the label.
        style (str): The style to be applied to the label
                     (e.g., "SideBarHeading", "SideBarText").
        *args: Additional positional arguments to be passed to the tk.Label
               constructor.
        **kwargs: Additional keyword arguments to be passed to the tk.Label
                  constructor.

    Returns:
        tk.Label: The configured Tkinter label widget.
    """
    if style == "SideBarHeading":
        return tk.Label(
            parent,
            text=text,
            font=(".AppleSystemUIFont", 18, "bold"),
            background=colours.off_black_100,
            *args,
            **kwargs
        )
    if style == "SideBarText":
        return tk.Label(
            parent,
            text=text,
            font=(".AppleSystemUIFont", 12),
            background=colours.off_black_100,
            *args,
            **kwargs
        )
    elif style == "PageHeading2":
        return tk.Label(
            parent,
            text=text,
            font=(".AppleSystemUIFont", 12, "bold"),
            background=colours.off_black_80,
            *args,
            **kwargs
        )
    elif style == "PageText":
        return tk.Label(
            parent,
            text=text,
            font=(".AppleSystemUIFont", 12),
            background=colours.off_black_80,
            *args,
            **kwargs
        )


def configure_styles(root):
    """
    Configures the styles for various Tkinter widgets.

    Parameters:
        root (tk.Tk): The root Tkinter window.

    Returns:
        None
    """
    set_theme("dark")
    style = ttk.Style(root)
    style.configure(
        "Heading.TLabel",
        foreground=colours.white,
        font=(".AppleSystemUIFont", 18, "bold"),
    )
    style.configure(
        "Label.TLabel",
        foreground=colours.white,
        font=(".AppleSystemUIFont", 12),
    )
    style.configure(
        "Label.TButton",
        foreground=colours.white,
        background="#232323",
        font=(".AppleSystemUIFont", 12),
    )
    style.configure(
        "Label.TCheckbutton",
        foreground=colours.white,
        background=colours.off_black_80,
        font=(".AppleSystemUIFont", 12),
    )
    style.configure(
        "Label.TMenubutton",
        foreground=colours.white,
        font=(".AppleSystemUIFont", 12),
    )
    style.configure(
        "Heading2.TLabel",
        foreground=colours.white,
        font=(".AppleSystemUIFont", 12, "bold"),
    )
    style.configure(
        "SelectedLabel.TLabel",
        foreground="#000000",
        font=(".AppleSystemUIFont", 12),
    )

    logging.info("Styles configured successfully for the root window.")
