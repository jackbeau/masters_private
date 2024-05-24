from audio_recorder import AudioToTextRecorder
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from jiwer import wer
import wave

# Global variable to store full sentences for calculating WER later
full_sentences = []

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

def text_detected(text):
    global displayed_text
    sentences_with_style = [
        f"{sentence + '' + sentence} "
        for i, sentence in enumerate(full_sentences)
    ]
    new_text = "".join(sentences_with_style).strip() + " " + text if len(sentences_with_style) > 0 else text

    if new_text != displayed_text:
        displayed_text = new_text
        clear_console()
        print(displayed_text, end="", flush=True)

def process_text(text):
    global full_sentences
    full_sentences.append(text)

def read_audio_file(file_path, chunk_size=1024):
    with wave.open(file_path, 'rb') as wf:
        while True:
            data = wf.readframes(chunk_size)
            if not data:
                break
            yield data

def run_experiment(model, beam_size, compute_type, audio_file):
    global full_sentences
    full_sentences = []  # Clear previous results

    recorder_config = {
        'model': model,
        'language': 'en',
        'webrtc_sensitivity': 2,
        'post_speech_silence_duration': 0.4,
        'min_length_of_recording': 0,
        'min_gap_between_recordings': 0,
        "ensure_sentence_starting_uppercase": False,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.2,
        'realtime_model_type': model,
        'on_realtime_transcription_update': text_detected, 
        "use_microphone": False,  # Disable microphone
        "compute_type": compute_type,
        "beam_size_realtime": beam_size
    }

    recorder = AudioToTextRecorder(**recorder_config)

    clear_console()
    print("Processing audio file...", end="", flush=True)

    start_time = time.time()
    for chunk in read_audio_file(audio_file):
        recorder.feed_audio(chunk)
    end_time = time.time()
    latency = end_time - start_time

    # Simulated reference text for WER calculation
    reference_text = "This is a sample reference text for WER calculation."
    hypothesis_text = " ".join(full_sentences)
    error_rate = wer(reference_text, hypothesis_text)

    # Simulate resource utilization metrics
    resource_utilization = np.random.uniform(50, 90)  # Placeholder

    return error_rate, latency, resource_utilization

# Step 2: Define Experiment Settings and Run Experiments
models = ['tiny.en', 'small.en']
beam_sizes = [1, 5, 10]
compute_types = ['int8_float32', 'float32']
audio_file = 'path_to_your_audio_file.wav'

results = []

for model in models:
    for beam_size in beam_sizes:
        for compute_type in compute_types:
            error_rate, latency, resource_utilization = run_experiment(model, beam_size, compute_type, audio_file)
            results.append({
                'model': model,
                'beam_size': beam_size,
                'compute_type': compute_type,
                'error_rate': error_rate,
                'latency': latency,
                'resource_utilization': resource_utilization
            })

# Step 3: Plot Results

def plot_results(results):
    # Convert results to structured arrays for easy plotting
    import pandas as pd
    df = pd.DataFrame(results)

    # Plot WER vs. Beam Size for Different Models
    plt.figure()
    for model in df['model'].unique():
        subset = df[df['model'] == model]
        plt.plot(subset['beam_size'], subset['error_rate'], label=model)
    plt.xlabel('Beam Size')
    plt.ylabel('WER')
    plt.title('WER vs. Beam Size for Different Models')
    plt.legend()
    plt.show()

    # Plot Latency vs. Beam Size for Different Models
    plt.figure()
    for model in df['model'].unique():
        subset = df[df['model'] == model]
        plt.plot(subset['beam_size'], subset['latency'], label=model)
    plt.xlabel('Beam Size')
    plt.ylabel('Latency (s)')
    plt.title('Latency vs. Beam Size for Different Models')
    plt.legend()
    plt.show()

    # Plot WER vs. Latency for Different Models
    plt.figure()
    for model in df['model'].unique():
        subset = df[df['model'] == model]
        plt.scatter(subset['latency'], subset['error_rate'], label=model)
    plt.xlabel('Latency (s)')
    plt.ylabel('WER')
    plt.title('WER vs. Latency for Different Models')
    plt.legend()
    plt.show()

plot_results(results)
