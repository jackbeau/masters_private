from faster_whisper import WhisperModel
import time
import librosa
import os
from audio_buffer import AudioBuffer
import numpy as np
import wave
import pyaudio
from thefuzz import fuzz

def stt(model, script):

    start = time.time()

    audio_buffer = AudioBuffer()
    audio_buffer.start()
    audio = pyaudio.PyAudio()

    while True:
        # print(audio_buffer.frames)

        start = time.time()
        print("\n ##### START #######")

        waveFile = wave.open("output.wav", 'wb')
        waveFile.setnchannels(1)
        waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        waveFile.setframerate(41000)
        waveFile.writeframes(b''.join(audio_buffer.frames))
        waveFile.close() 

        audio_path = "/Users/jackbeaumont/Code/Master/project/project/output.wav"
        audio_file_path = os.fspath(audio_path)
        audio_array, sr = librosa.load(audio_file_path, sr=16_000)

        print("audio_buffer.frames")
        print("".join(audio_buffer.frames))

        print("audio_array")
        print(audio_array)

        end = time.time()
        print("save time: ") # 0.009
        print(end-start)
        start2=time.time()

        # transcribe(audio_array, model)
        transcribe(audio_array, model, script)

        end = time.time()
        print("Master transcribe: ")
        print(end-start2)
        print("Total time: ") #1.3s
        print(end-start)

def search_with_similarity(text, target_string):

    start_time = time.time()
    lines = text.split('\n')  # Split text into lines, adjust as needed

    best_score = 0
    match = ""

    for line in lines:
        similarity_score = fuzz.partial_ratio(line.lower(), target_string.lower())

        if similarity_score > best_score:
            best_score = similarity_score
            match = line
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Time elapsed: {elapsed_time} seconds')
        
    print(f"Best match: '{match.strip()}' (Similarity: {best_score}%)")


def transcribe(audio, model, script):
    segments, info = model.transcribe(audio, language="en")

    target_string = ""

    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        target_string += segment.text
    
    search_with_similarity(script, " ".join(target_string.split()[-5:]))


if __name__ == '__main__':
    
    model_size = "tiny.en"
    model = WhisperModel(model_size, compute_type='float32')
    script = open('script.txt', 'r')
    large_text = script.read()

    stt(model, large_text)