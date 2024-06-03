import os
import time
import logging
import csv
from jiwer import wer, mer, wil, wip, cer

# Import transcription classes
from transcribe_faster_whisper import FasterWhisperModel
from transcribe_seamlessM4T import SeamlessM4TModelClass
from transcribe_whisper import WhisperModelClass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths
data_dir = 'labs/experiment_dataset'
results_dir = 'labs/results'

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

def run_experiment(segments, transcribe_model, model_name):
    results = []
    for audio_path, true_transcription in segments:
        try:
            audio_start_time = time.time()
            predicted_transcription = transcribe_model.transcribe(audio_path)
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
    transcription_tools = [
        (FasterWhisperModel('tiny.en'), 'faster_whisper_tiny'),
        (FasterWhisperModel('base.en'), 'faster_whisper_base'),
        (FasterWhisperModel('small.en'), 'faster_whisper_small'),
        (FasterWhisperModel('medium.en'), 'faster_whisper_medium'),
        (FasterWhisperModel('large'), 'faster_whisper_large'),
        (FasterWhisperModel('distil-small.en'), 'faster_distil_whisper_small'),
        (FasterWhisperModel('distil-medium.en'), 'faster_distil_whisper_medium'),
        (FasterWhisperModel('distil-large-v2'), 'faster_distil_whisper_largev2'),
        (FasterWhisperModel('distil-large-v3'), 'faster_distil_whisper_largev3'),
        (SeamlessM4TModelClass(), 'seamlessM4T_medium'),
        (WhisperModelClass('tiny.en'), 'whisper_tiny'),
        (WhisperModelClass('base.en'), 'whisper_base'),
        (WhisperModelClass('small.en'), 'whisper_small'),
        (WhisperModelClass('medium.en'), 'whisper_medium'),
        (WhisperModelClass('large'), 'whisper_large')
    ]

    for transcribe_model, model_name in transcription_tools:
        logging.info(f'Starting transcription with {model_name}')
        results = run_experiment(segments, transcribe_model, model_name)
        results_file = os.path.join(results_dir, f'transcription_results_{model_name}.csv')
        save_results_to_csv(results, results_file)
        logging.info(f'Completed transcription with {model_name}')

if __name__ == '__main__':
    main()
