import librosa
import noisereduce as nr
import numpy as np

class AudioCleanup:
    def __init__(self, audio_path):
        self.audio_path = audio_path

    def reduce_noise(self):
        audio_array, sr = librosa.load(self.audio_path, sr=16000)
        reduced_noise = nr.reduce_noise(y=audio_array, sr=sr)
        return reduced_noise

    def to_int16(self, audio_array):
        return np.int16(audio_array / np.max(np.abs(audio_array)) * 32767)
