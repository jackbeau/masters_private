"""
File: get_devices.py
Author: Jack Beaumont
Date: 2024-01-26

Description: Helper tool to find local microphone inputs.
"""

import pyaudio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("get_devices")
logger.setLevel(logging.INFO)


def list_audio_devices():
    """
    List all audio input devices available on the system.

    This function prints the index, name, and maximum input channels of each
    audio device.
    """
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        logger.info(
            "Device %d: %s (Max Input Channels: %d)",
            i,
            dev["name"],
            dev["maxInputChannels"],
        )


if __name__ == "__main__":
    list_audio_devices()
