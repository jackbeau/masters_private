import pyaudio
import wave
import tempfile
import os
import logging
import numpy as np
from multiprocessing import Process, Queue, Event
import threading

class AudioBuffer:
    RATE = 16000
    BUFFER_SIZE = 1024

    def __init__(self, input_device_index, frames_queue, stop_event):
        self.input_device_index = input_device_index
        self.frames_queue = frames_queue
        self.stop_event = stop_event
        self.project_temp_dir = os.path.join(os.getcwd(), 'temp_audio_files')
        os.makedirs(self.project_temp_dir, exist_ok=True)
        self.original_wave_file_path = None
        self.noise_reduced_wave_file_path = None
        self.is_recording = False

    def start_recording(self):
        self.setup_audio_files()
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.BUFFER_SIZE,
                                      input_device_index=self.input_device_index)

        try:
            while not self.stop_event.is_set():
                data = self.stream.read(self.BUFFER_SIZE)
                self.frames_queue.put(data)
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

    def stop_recording(self):
        self.stop_event.set()

    def setup_audio_files(self):
        with tempfile.NamedTemporaryFile(suffix='original.wav', delete=False, dir=self.project_temp_dir) as temp_wav_file:
            self.original_wave_file_path = temp_wav_file.name
            logging.info(f"Temporary original audio file path: {self.original_wave_file_path}")
        with tempfile.NamedTemporaryFile(suffix='cleaned.wav', delete=False, dir=self.project_temp_dir) as temp_wav_file:
            self.noise_reduced_wave_file_path = temp_wav_file.name
            logging.info(f"Temporary noise-reduced audio file path: {self.noise_reduced_wave_file_path}")

    def save_original_audio(self):
        frames = []
        while not self.frames_queue.empty():
            frames.append(self.frames_queue.get())

        with wave.open(self.original_wave_file_path, 'wb') as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(self.RATE)
            wave_file.writeframes(b''.join(frames))

    def load_audio(self):
        audio_array, sr = librosa.load(self.original_wave_file_path, sr=self.RATE)
        return audio_array

    def save_noise_reduced_audio(self, audio_array):
        with wave.open(self.noise_reduced_wave_file_path, 'wb') as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(self.RATE)
            wave_file.writeframes(audio_array.tobytes())
