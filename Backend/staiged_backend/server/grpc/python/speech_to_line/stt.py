from faster_whisper import WhisperModel

class STT:
    def __init__(self, model_size="tiny.en"):
        self.model = WhisperModel(model_size, compute_type='float32')

    def transcribe(self, audio_array):
        segments, _ = self.model.transcribe(audio_array, language="en")
        return segments
