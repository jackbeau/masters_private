import os
import time
import logging
import csv
import pandas as pd
from jiwer import wer, mer, wil, wip, cer
from faster_whisper import WhisperModel

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths
data_dir = 'labs/experiment_dataset/'
results_dir = 'labs/results/faster_whisper_base'

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

def read_segments(data_dir):
    segments = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.wav'):
                audio_path = os.path.join(root, file)
                transcription_path = audio_path.replace('.wav', '.txt')
                if not os.path.exists(transcription_path):
                    logging.warning(f'Transcription file not found for audio file: {audio_path}')
                    continue
                with open(transcription_path, 'r') as f:
                    transcription = f.read().strip()
                segments.append((audio_path, transcription))
    return segments

def run_experiment(segments, model_size, device, compute_type, beam_size, cpu_threads):
    results = []
    model_name = f'faster_whisper_{model_size}_{device}_{compute_type}_beam{beam_size}_threads{cpu_threads}'
    model = WhisperModel(model_size, device=device, compute_type=compute_type, cpu_threads=cpu_threads)

    for audio_path, true_transcription in segments:
        try:
            audio_start_time = time.time()
            segments, info = model.transcribe(audio_path, beam_size=beam_size)
            predicted_transcription = ' '.join([segment.text for segment in segments])
            audio_end_time = time.time()

            latency = audio_end_time - audio_start_time

            metrics = {
                'wer': wer(true_transcription, predicted_transcription),
                'mer': mer(true_transcription, predicted_transcription),
                'wil': wil(true_transcription, predicted_transcription),
                'wip': wip(true_transcription, predicted_transcription),
                'cer': cer(true_transcription, predicted_transcription),
            }

            result = [
                audio_path,
                model_name,
                true_transcription,
                predicted_transcription,
                latency,
                metrics['wer'],
                metrics['mer'],
                metrics['wil'],
                metrics['wip'],
                metrics['cer']
            ]
            results.append(result)
            logging.info(f'Processed {audio_path} with {model_name}: WER={metrics["wer"]:.4f}, Latency={latency:.4f}s')

        except Exception as e:
            logging.error(f'Error processing {audio_path} with {model_name}: {e}')

    return results

def save_aggregated_results_to_csv(aggregated_results, results_file):
    header = ['model', 'beam_size', 'cpu_threads', 'latency_mean', 'latency_std', 'wer_mean', 'wer_std']

    with open(results_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(header)
        csvwriter.writerows(aggregated_results)
    logging.info(f'Aggregated results saved to {results_file}')

def main():
    segments = read_segments(data_dir)
    configurations = []

    # Varying cpu_threads with constant beam_size
    constant_beam_size = 1
    for cpu_threads in range(1, 11):
        configurations.append(('base.en', 'cpu', 'int16', constant_beam_size, cpu_threads))

    # Varying beam_size with constant cpu_threads
    constant_cpu_threads = 4
    for beam_size in range(1, 11):
        configurations.append(('base.en', 'cpu', 'int16', beam_size, constant_cpu_threads))

    aggregated_results = []

    for model_size, device, compute_type, beam_size, cpu_threads in configurations:
        logging.info(f'Starting transcription with config: {model_size}, {device}, {compute_type}, beam_size={beam_size}, cpu_threads={cpu_threads}')
        results = run_experiment(segments, model_size, device, compute_type, beam_size, cpu_threads)

        # Convert results to DataFrame
        df_results = pd.DataFrame(results, columns=['audio_path', 'model', 'true_transcription', 'predicted_transcription', 'latency', 'wer', 'mer', 'wil', 'wip', 'cer'])

        # Calculate mean and standard deviation
        latency_mean = df_results['latency'].mean()
        latency_std = df_results['latency'].std()
        wer_mean = df_results['wer'].mean()
        wer_std = df_results['wer'].std()

        aggregated_results.append([f'faster_whisper_{model_size}_{device}_{compute_type}_beam{beam_size}_threads{cpu_threads}', beam_size, cpu_threads, latency_mean, latency_std, wer_mean, wer_std])

        logging.info(f'Completed transcription with config: {model_size}, {device}, {compute_type}, beam_size={beam_size}, cpu_threads={cpu_threads}')

    # Save aggregated results to CSV
    results_file = os.path.join(results_dir, 'transcription_aggregated_results.csv')
    save_aggregated_results_to_csv(aggregated_results, results_file)

if __name__ == '__main__':
    main()
