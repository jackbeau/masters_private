import os
import time
import numpy as np
import matplotlib.pyplot as plt
from jiwer import wer
from sphfile import SPHFile
from audio_recorder import AudioToTextRecorder
from colorama import Fore, Back, Style
import colorama
import logging
import wave
import pyaudio
import multiprocessing

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the TED-LIUM dataset
data_dir = '/Users/jackb/Downloads/TEDLIUM_release-3/TEDLIUM_release-3/data'

def parse_stm_file(filepath):
    transcriptions = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith(';;') or line.strip() == "":
                continue
            parts = line.strip().split(maxsplit=5)
            if len(parts) < 6:
                continue
            transcript = parts[5]
            transcriptions.append(transcript)
    return ' '.join(transcriptions)

def read_tedlium_data(data_dir, max_files=10):
    sph_dir = os.path.join(data_dir, 'sph')
    stm_dir = os.path.join(data_dir, 'stm')

    audio_files = []
    transcriptions = []
    files_processed = 0

    logging.info('Reading TED-LIUM data...')

    for root, _, files in os.walk(sph_dir):
        for file in files:
            if file.endswith('.sph'):
                audio_path = os.path.join(root, file)
                transcription_path = os.path.join(stm_dir, file.replace('.sph', '.stm'))
                wav_path = audio_path.replace('.sph', '.wav')

                # Check if the corresponding transcription file exists
                if not os.path.exists(transcription_path):
                    logging.warning(f'Transcription file not found for audio file: {audio_path}')
                    continue

                # Convert SPH to WAV
                sph = SPHFile(audio_path)
                sph.write_wav(wav_path)

                # Load audio file
                with wave.open(wav_path, 'rb') as wf:
                    audio_data = wf.readframes(wf.getnframes())
                    audio_files.append((wav_path, audio_data))
                    logging.info(f'Converted and read audio file: {wav_path}')

                # Load and parse transcription
                transcription = parse_stm_file(transcription_path)
                transcriptions.append((transcription_path, transcription))
                logging.info(f'Read transcription file: {transcription_path}')

                files_processed += 1
                if files_processed >= max_files:
                    return audio_files, transcriptions

    return audio_files, transcriptions

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

def text_detected(text):
    global full_sentences
    global displayed_text

    new_text = full_sentences + " " + text if len(full_sentences) > 0 else text

    if new_text != displayed_text:
        displayed_text = new_text
        clear_console()
        print(displayed_text, end="", flush=True)

def process_text(text):
    print("test")
    print(text)
    global full_sentences
    full_sentences = text
    text_detected("")

def play_audio(audio_path):
    p = pyaudio.PyAudio()
    wf = wave.open(audio_path, 'rb')

    # Open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks
    chunk_size = 1024
    data = wf.readframes(chunk_size)

    while data:
        stream.write(data)
        data = wf.readframes(chunk_size)

    stream.stop_stream()
    stream.close()
    p.terminate()

def run_experiment(model, beam_size, compute_type, audio_path, transcription):
    global full_sentences
    full_sentences = ""  # Clear previous results

    logging.info(f'Running experiment with model={model}, beam_size={beam_size}, compute_type={compute_type}')

    recorder_config = {
        'model': 'tiny.en',
        'language': 'en',
        'webrtc_sensitivity': 2,
        'post_speech_silence_duration': 0.4,
        'min_length_of_recording': 0,
        'min_gap_between_recordings': 0,
        "ensure_sentence_starting_uppercase": False,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.2,
        'realtime_model_type': 'tiny.en',
        'on_realtime_transcription_update': text_detected,
        "input_device_index": 1,
        "compute_type": "int8_float32",
        "beam_size_realtime": 5
        # 'on_realtime_transcription_stabilized': text_detected,
    }

    recorder = AudioToTextRecorder(**recorder_config)

    clear_console()
    print("Processing audio file...", end="", flush=True)

    try:
        audio_process = multiprocessing.Process(target=play_audio, args=(audio_path,))
        audio_process.start()

        start_time = time.time()

        while audio_process.is_alive():
            print("loop")
            recorder.text(process_text)
            time.sleep(0.1)  # Adjust as needed for real-time processing

        audio_process.join()

        recorder.shutdown()  # Ensure the recorder is properly shut down

        end_time = time.time()
        latency = end_time - start_time

        hypothesis_text = full_sentences.strip()
        error_rate = wer(transcription, hypothesis_text)

        logging.info(f'Experiment results - WER: {error_rate}, Latency: {latency}s')

        # Simulate resource utilization metrics
        resource_utilization = np.random.uniform(50, 90)  # Placeholder

        return error_rate, latency, resource_utilization

    except Exception as e:
        logging.error(f'Error running experiment: {e}')
        return None, None, None

def main():
    audio_files, transcriptions = read_tedlium_data(data_dir, max_files=10)

    # Global variable to store full sentences for calculating WER later
    global full_sentences
    global displayed_text
    full_sentences = []
    displayed_text = ""

    # Define Experiment Settings and Run Experiments
    models = ['tiny.en', 'small.en']
    beam_sizes = [1, 5, 10]
    compute_types = ['int8_float32', 'float32']

    results = []

    for model in models:
        for beam_size in beam_sizes:
            for compute_type in compute_types:
                for (audio_path, audio_data), (transcription_path, transcription) in zip(audio_files, transcriptions):
                    error_rate, latency, resource_utilization = run_experiment(model, beam_size, compute_type, audio_path, transcription)
                    if error_rate is not None:
                        results.append({
                            'model': model,
                            'beam_size': beam_size,
                            'compute_type': compute_type,
                            'error_rate': error_rate,
                            'latency': latency,
                            'resource_utilization': resource_utilization
                        })

    # Check if results are collected
    if not results:
        logging.warning("No results collected. Please check the experiment setup.")
    else:
        logging.info(f"Total experiments run: {len(results)}")

    # Plot Results
    def plot_results(results):
        if not results:
            logging.warning("No results to plot.")
            return

        # Convert results to numpy arrays for easy plotting
        models = list(set([r['model'] for r in results]))
        beam_sizes = sorted(list(set([r['beam_size'] for r in results])))

        logging.info('Plotting results...')

        # Plot WER vs. Beam Size for Different Models
        plt.figure()
        for model in models:
            model_results = [r for r in results if r['model'] == model]
            beam_sizes = [r['beam_size'] for r in model_results]
            error_rates = [r['error_rate'] for r in model_results]
            if beam_sizes and error_rates:
                plt.plot(beam_sizes, error_rates, label=model)
        plt.xlabel('Beam Size')
        plt.ylabel('WER')
        plt.title('WER vs. Beam Size for Different Models')
        plt.legend()
        plt.show()

        # Plot Latency vs. Beam Size for Different Models
        plt.figure()
        for model in models:
            model_results = [r for r in results if r['model'] == model]
            beam_sizes = [r['beam_size'] for r in model_results]
            latencies = [r['latency'] for r in model_results]
            if beam_sizes and latencies:
                plt.plot(beam_sizes, latencies, label=model)
        plt.xlabel('Beam Size')
        plt.ylabel('Latency (s)')
        plt.title('Latency vs. Beam Size for Different Models')
        plt.legend()
        plt.show()

        # Plot WER vs. Latency for Different Models
        plt.figure()
        for model in models:
            model_results = [r for r in results if r['model'] == model]
            latencies = [r['latency'] for r in model_results]
            error_rates = [r['error_rate'] for r in model_results]
            if latencies and error_rates:
                plt.scatter(latencies, error_rates, label=model)
        plt.xlabel('Latency (s)')
        plt.ylabel('WER')
        plt.title('WER vs. Latency for Different Models')
        plt.legend()
        plt.show()

    plot_results(results)

if __name__ == '__main__':
    main()
