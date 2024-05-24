import logging
from faster_whisper import WhisperModel

class SpeechToText:
    def __init__(self, model_size="tiny.en"):
        self.model = WhisperModel(model_size, compute_type='float32')

    def transcribe(self, audio_array):
        segments, info = self.model.transcribe(audio_array, language="en")
        target_string = ""

        for segment in segments:
            logging.info("[%.2fs -> %.2fs] %s" % (
                segment.start,
                segment.end,
                segment.text)
            )
            target_string += segment.text

        return target_string
