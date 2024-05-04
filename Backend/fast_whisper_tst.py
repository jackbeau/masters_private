from faster_whisper import WhisperModel

model_size = "tiny.en"

model = WhisperModel(model_size, device="cpu", cpu_threads=8, compute_type="float32")

segments, _ = model.transcribe(
    "short_audio.mp3",
    language="en",
    beam_size=1,
    temperature=0,
    suppress_tokens=None
)

segments = list(segments)