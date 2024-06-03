from transformers import AutoProcessor, SeamlessM4TModel
import torchaudio

class SeamlessM4TModelClass:
    def __init__(self):
        self.processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
        self.model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")

    def transcribe(self, audio_path):
        audio, orig_freq = torchaudio.load(audio_path)
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16000)
        audio_inputs = self.processor(audios=audio, return_tensors="pt")
        output_tokens = self.model.generate(**audio_inputs, tgt_lang="eng", generate_speech=False)
        transcribed_text = self.processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
        return transcribed_text
