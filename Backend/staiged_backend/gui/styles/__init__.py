import tkinter as tk
from tkinter import ttk
from gui.styles.theme.sv_ttk import set_theme

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
    if style == "SideBarHeading":
        return tk.Label(
            parent, text=text, font=(".AppleSystemUIFont", 18, "bold"), background=colours.off_black_100, *args, **kwargs
        )
    if style == "SideBarText":
        return tk.Label(
            parent, text=text, font=(".AppleSystemUIFont", 12), background=colours.off_black_100, *args, **kwargs
        )
    elif style == "PageHeading2":
        return tk.Label(
            parent, text=text, font=(".AppleSystemUIFont", 12, "bold"), background=colours.off_black_80, *args, **kwargs
        )
    elif style == "PageText":
        return tk.Label(
            parent, text=text, font=(".AppleSystemUIFont", 12), background=colours.off_black_80, *args, **kwargs
        )


def configure_styles(root):
    set_theme("dark")
    style = ttk.Style(root)
    style.configure("Heading.TLabel", foreground=colours.white, font=(".AppleSystemUIFont", 18, "bold"))
    style.configure("Label.TLabel", foreground=colours.white, font=(".AppleSystemUIFont", 12))
    style.configure("Label.TButton", foreground=colours.white, background='#232323', font=(".AppleSystemUIFont", 12))
    style.configure('Label.TCheckbutton', foreground=colours.white, background=colours.off_black_80, font=(".AppleSystemUIFont", 12))
    style.configure("Label.TMenubutton", foreground=colours.white, font=(".AppleSystemUIFont", 12))
    style.configure("Heading2.TLabel", foreground=colours.white, font=(".AppleSystemUIFont", 12, "bold"))
    style.configure("SelectedLabel.TLabel", foreground="#000000", font=(".AppleSystemUIFont", 12))