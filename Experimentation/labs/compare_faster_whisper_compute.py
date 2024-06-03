import os
import time
import logging
import csv
from jiwer import wer, mer, wil, wip, cer

# Import transcription class
from faster_whisper import WhisperModel

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths
data_dir = 'labs/experiment_dataset'
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

def run_experiment(segments, model_size, device, compute_type):
    results = []
    model_name = f'faster_whisper_{model_size}_{device}_{compute_type}'
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    for audio_path, true_transcription in segments:
        try:
            audio_start_time = time.time()
            segments, info = model.transcribe(audio_path, beam_size=1)
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

def save_results_to_csv(results, results_file):
    header = ['audio_path', 'model', 'true_transcription', 'predicted_transcription', 'latency', 'wer', 'mer', 'wil', 'wip', 'cer']

    with open(results_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(header)
        csvwriter.writerows(results)
    logging.info(f'Results saved to {results_file}')

def main():
    segments = read_segments(data_dir)
    configurations = [
        ('base.en', 'cpu', 'int16'),
        ('base.en', 'cpu', 'int8')
    ]

    for model_size, device, compute_type in configurations:
        logging.info(f'Starting transcription with config: {model_size}, {device}, {compute_type}')
        results = run_experiment(segments, model_size, device, compute_type)
        results_file = os.path.join(results_dir, f'transcription_results_{model_size}_{device}_{compute_type}.csv')
        save_results_to_csv(results, results_file)
        logging.info(f'Completed transcription with config: {model_size}, {device}, {compute_type}')

if __name__ == '__main__':
    main()
