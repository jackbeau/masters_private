"""
File: audio_buffer.py
Author: Jack Beaumont
Date: 2024-01-26

Description: An audio buffer for continuously storing a window of audio of
constant width from an audio source."
"""

import pyaudio
import numpy as np
from collections import deque
import threading
import logging
import time

# Set up logging to display information messages
logging.basicConfig(level=logging.INFO)

class AudioBuffer:
    RATE = 44100  # Samples collected per second
    CHUNK = 2048  # Number of frames in the buffer

    def __init__(self, max_chunks: int = 200, input_device_index: int = 1) -> None:
        """
        Initialize the AudioBuffer instance.

        Parameters:
            max_chunks (int): Maximum number of chunks to store in the buffer.
            input_device_index (int): Index of the input audio device.
        """
        self.max_chunks = max_chunks
        self.input_device_index = input_device_index
        self.frames = deque(maxlen=max_chunks)
        self.stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            input_device_index=self.input_device_index
        )
        self.thread = threading.Thread(target=self._collect_data, daemon=True)

    def __call__(self):
        return np.concatenate(self.frames)

    def __len__(self):
        return self.CHUNK * self.max_chunks

    def duration(self):
        duration_seconds = round(self.CHUNK * self.max_chunks / self.RATE, 2)
        minutes, seconds = divmod(duration_seconds, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        formatted_duration = "{:02}:{:02}.{:02}".format(int(minutes), int(seconds), milliseconds)
        return formatted_duration

    def is_full(self):
        return len(self.frames) == self.max_chunks

    def start(self):
        self.thread.start()
        while not self.is_full():
            time.sleep(0.1)

    def stop(self):
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()

    def _collect_data(self):
        try:
            while True:
                raw_data = self.stream.read(self.CHUNK)
                decoded = np.frombuffer(raw_data, np.int16)
                self.frames.append(decoded)
        except OSError as e:
            if e.errno == -9981:  # Input overflowed error
                logging.warning("Input overflowed. Ignoring new packets.")
            else:
                logging.error(f"Error in _collect_data: {e}")

if __name__ == "__main__":
    audio_buffer = AudioBuffer(input_device_index=1)
    audio_buffer.start()

    try:
        while not audio_buffer.is_full():
            time.sleep(0.1)

        frames_count = len(audio_buffer())
        frames_shape = audio_buffer().shape
        frames_info = f"Collected {frames_count} frames with shape {frames_shape}"
        logging.info(frames_info)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received. Stopping the audio buffer.")
        audio_buffer.stop()
