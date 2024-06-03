from faster_whisper import WhisperModel
import torch
from transformers import AutoProcessor, SeamlessM4TModel
import torchaudio
from transcription_model import TranscriptionModel

class FasterWhisperModel(TranscriptionModel):
    def __init__(self, model_size):
        self.model = WhisperModel(model_size)
    
    def transcribe(self, audio_path):
        segments, info = self.model.transcribe(audio_path, beam_size=1)
        transcription = ' '.join([segment.text for segment in segments])
        return transcription