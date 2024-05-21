"""
File: get_devices.py
Author: Jack Beaumont
Date: 2024-01-26

Description: Helper tool to find local microphone inputs."
"""

import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print((i, dev['name'], dev['maxInputChannels']))
