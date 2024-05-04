from faster_whisper import WhisperModel
import time
import librosa
import os
import numpy as np
import wave
import pyaudio


def stt(path, model):
    # Extract the first 10 seconds of audio
    window_size = 10
    window_hop = .5

    start = time.time()

    windows=0

    while True:

        if time.time() - start > window_hop:
        
            samples_to_keep = int((window_size+window_hop*windows) * sr)
            audio_segments = audio_array[samples_to_keep:2*samples_to_keep]

            transcribe(path, model)

            start = time.time()
            windows += 1


def transcribe(audio, model):
    start = time.time()
    segments, info = model.transcribe(audio, language="en")
    end = time.time()
    print(end-start)

    print(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability)
    )

    print(segments)

    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    print("Finished fw")


if __name__ == '__main__':
    audio_path = "/Users/jackbeaumont/Code/Master/project/project/output.wav"

    audio_file_path = os.fspath(audio_path)
    audio_array, sr = librosa.load(audio_file_path, sr=16_000)
    
    model_size = "tiny.en"
    model = WhisperModel(model_size, compute_type='float32')

    stt(audio_array, model)