import whisper

from transcription_model import TranscriptionModel


class WhisperModelClass:
    def __init__(self, model_name):
        self.model = whisper.load_model(model_name)
    
    def transcribe(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result['text']
