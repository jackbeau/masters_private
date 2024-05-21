"""
File: audio_buffer.py
Author: Jack Beaumont
Date: 2024-01-26

Description: A audio buffer for continously storing a window of audio of
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

    def __init__(self, max_chunks: int = 200) -> None:
        """
        Initialize the AudioBuffer instance.

        Parameters:
            max_chunks (int): Maximum number of chunks to store in the buffer.
        """
        # Initialize the AudioBuffer instance with specified parameters
        self.max_chunks = max_chunks
        # Use a deque to store audio frames, limiting its length to maxlen
        self.frames = deque(maxlen=max_chunks)
        # Open an audio stream for input using PyAudio
        self.stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            input_device_index=1
        )
        # Create a thread for collecting audio data
        self.thread = threading.Thread(target=self._collect_data, daemon=True)

    def __call__(self):
        """
        When the instance is called, concatenate the stored audio frames.

        Returns:
            np.ndarray: Concatenated audio frames.
        """
        return np.concatenate(self.frames)

    def __len__(self):
        """
        Define the length of the instance.

        Returns:
            int: Length of the audio buffer.
        """
        return self.CHUNK * self.max_chunks

    def duration(self):
        """
        Calculate and format the duration of audio.

        Returns:
            str: Formatted duration of audio.
        """
        duration_seconds = round(self.CHUNK * self.max_chunks / self.RATE, 2)

        # Format duration
        minutes, seconds = divmod(duration_seconds, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        formatted_duration = "{:02}:{:02}.{:02}".format(
            int(minutes),
            int(seconds),
            milliseconds
            )

        return formatted_duration

    def is_full(self):
        """
        Check if the deque is full.

        Returns:
            bool: True if the buffer is full, False otherwise.
        """
        return len(self.frames) == self.max_chunks

    def start(self):
        """Start collecting audio data in a separate thread."""
        self.thread.start()
        while not self.is_full():
            time.sleep(0.1)

    def stop(self):
        """Stop the data collection thread and close the audio stream."""
        self.thread.join()  # Wait for the thread to finish before exiting
        self.stream.stop_stream()
        self.stream.close()

    def _collect_data(self):
        """Collect audio data in a separate thread."""
        try:
            while True:
                # Get audio chunk and append to frames
                raw_data = self.stream.read(self.CHUNK)
                decoded = np.frombuffer(raw_data, np.int16)
                self.frames.append(decoded)
        except OSError as e:
            if e.errno == -9981:  # Input overflowed error
                logging.warning("Input overflowed. Ignoring new packets.")
                # Optionally, you can clear the frames or take other action here
            else:
                logging.error(f"Error in _collect_data: {e}")

if __name__ == "__main__":
    # Create an instance of AudioBuffer
    audio_buffer = AudioBuffer()
    # Start collecting audio data in a separate thread
    audio_buffer.start()

    try:
        while not audio_buffer.is_full():
            time.sleep(0.1)

        # Log information about the collected audio frames
        frames_count = len(audio_buffer())
        frames_shape = audio_buffer().shape
        frames_info = (
            f"Collected {frames_count} frames with shape {frames_shape}"
        )
        logging.info(frames_info)

    except KeyboardInterrupt:
        # Handle KeyboardInterrupt and stop the audio buffer
        logging.info("KeyboardInterrupt received. Stopping the audio buffer.")
        audio_buffer.stop()
