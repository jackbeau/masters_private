"""
Audio Buffer Module

This module provides a class to handle audio buffering and recording using
PyAudio.
"""

import pyaudio
import numpy as np
from collections import deque
import threading
import logging
import time
import traceback

# Set up logging to display information messages
logging.basicConfig(level=logging.INFO)


class AudioBuffer:
    """
    A class to handle audio buffering and recording using pyaudio.

    Attributes:
        RATE (int): The sample rate of the audio.
        CHUNK (int): The number of frames in the buffer.
        max_chunks (int): The maximum number of chunks to store in the buffer.
        frames (deque): A deque to store audio frames.
        pa (pyaudio.PyAudio): The PyAudio instance.
        stream (pyaudio.Stream): The audio stream.
        thread (threading.Thread): The thread to collect audio data.
    """

    RATE = 44100  # Samples collected per second
    CHUNK = 2048  # Number of frames in the buffer

    def __init__(self, max_chunks: int = 200) -> None:
        """
        Initialize the AudioBuffer instance.

        Parameters:
            max_chunks (int): Maximum number of chunks to store in the buffer.
        """
        self.max_chunks = max_chunks
        self.frames = deque(maxlen=max_chunks)
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self._open_stream()
        self.thread = threading.Thread(target=self._collect_data, daemon=True)

    def _open_stream(self) -> None:
        """Helper method to open the audio stream."""
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            input_device_index=1,
        )

    def __call__(self) -> np.ndarray:
        """
        When the instance is called, concatenate the stored audio frames.

        Returns:
            np.ndarray: Concatenated audio frames.
        """
        return np.concatenate(self.frames)

    def __len__(self) -> int:
        """
        Define the length of the instance.

        Returns:
            int: Length of the audio buffer.
        """
        return self.CHUNK * self.max_chunks

    def duration(self) -> str:
        """
        Calculate and format the duration of audio.

        Returns:
            str: Formatted duration of audio.
        """
        duration_seconds = round(self.CHUNK * self.max_chunks / self.RATE, 2)
        minutes, seconds = divmod(duration_seconds, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        formatted_duration = "{:02}:{:02}.{:02}".format(
            int(minutes), int(seconds), milliseconds
        )
        return formatted_duration

    def is_full(self) -> bool:
        """
        Check if the deque is full.

        Returns:
            bool: True if the buffer is full, False otherwise.
        """
        return len(self.frames) == self.max_chunks

    def start(self) -> None:
        """Start collecting audio data in a separate thread."""
        self.thread.start()
        while not self.is_full():
            time.sleep(0.1)

    def stop(self) -> None:
        """Stop the data collection thread and close the audio stream."""
        self.thread.join()  # Wait for the thread to finish before exiting
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()

    def _collect_data(self) -> None:
        """Collect audio data in a separate thread."""
        try:
            while True:
                try:
                    # Get audio chunk and append to frames
                    raw_data = self.stream.read(self.CHUNK)
                    decoded = np.frombuffer(raw_data, np.int16)
                    self.frames.append(decoded)
                except OSError as e:
                    if e.errno == pyaudio.paInputOverflowed:
                        logging.warning("Input overflowed. Frame dropped.")
                    elif e.errno == -9988:  # Stream closed error
                        logging.warning(
                            "Stream closed. Attempting to restart."
                        )
                        self._restart_stream()
                    else:
                        logging.error(f"Error during recording: {e}")
                        tb_str = traceback.format_exc()
                        logging.error(f"Traceback: {tb_str}")
                        continue
                except Exception as e:
                    logging.error(f"Error during recording: {e}")
                    tb_str = traceback.format_exc()
                    logging.error(f"Traceback: {tb_str}")
                    continue
        finally:
            self._close_stream()

    def _restart_stream(self) -> None:
        """Restart the audio stream after it has been closed."""
        self._close_stream()
        time.sleep(0.5)  # Delay before restarting the stream
        self._open_stream()

    def _close_stream(self) -> None:
        """Helper method to close the audio stream."""
        try:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
        except OSError as e:
            logging.warning(f"Stream already closed: {e}")

    def __del__(self) -> None:
        """Ensure resources are cleaned up on deletion."""
        self._close_stream()
        if self.pa is not None:
            self.pa.terminate()


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
