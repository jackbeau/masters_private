import whisper
import io
import os
import librosa
import time

model = whisper.load_model("tiny.en")

path = "short_audio.mp3"

audio_file_path = os.fspath(path)

# Load the entire audio file
audio_array, sr = librosa.load(audio_file_path, sr=16_000)

# Extract the first 10 seconds of audio
duration = 1  # in seconds
samples_to_keep = int(duration * sr)
audio_segments = audio_array[:samples_to_keep]

start = time.time()
result = model.transcribe(audio_segments, fp16=False, language="en")
end = time.time()

print(result["text"])
print(end - start)
