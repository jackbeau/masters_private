import os
import logging
import random
from sphfile import SPHFile
from pydub import AudioSegment

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Relative paths
data_dir = '/Users/jackb/Downloads/TEDLIUM_release-3/TEDLIUM_release-3/data'
output_dir = 'labs/experiment_dataset'

def parse_stm_file(filepath):
    segments = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith(';;') or line.strip() == "":
                continue
            parts = line.strip().split(maxsplit=6)
            if len(parts) < 7:
                continue
            start_time = float(parts[3])
            end_time = float(parts[4])
            transcript = parts[6]
            segments.append((start_time, end_time, transcript))
    return segments

def read_and_prepare_data(data_dir, output_dir, num_segments=20):
    sph_dir = os.path.join(data_dir, 'sph')
    stm_dir = os.path.join(data_dir, 'stm')

    all_files = []

    logging.info('Reading TED-LIUM data...')

    for root, _, files in os.walk(sph_dir):
        for file in files:
            if file.endswith('.sph'):
                audio_path = os.path.join(root, file)
                transcription_path = os.path.join(stm_dir, file.replace('.sph', '.stm'))
                if os.path.exists(transcription_path):
                    all_files.append((audio_path, transcription_path))

    selected_files = random.sample(all_files, min(num_segments, len(all_files)))
    selected_segments = []

    for audio_path, transcription_path in selected_files:
        wav_path = audio_path.replace('.sph', '.wav')
        
        # Convert SPH to WAV
        sph = SPHFile(audio_path)
        sph.write_wav(wav_path)

        # Load and parse transcription with timings
        segments = parse_stm_file(transcription_path)
        if segments:
            selected_segment = random.choice(segments)
            selected_segments.append((wav_path, selected_segment))

    for i, (wav_path, (start_time, end_time, transcript)) in enumerate(selected_segments):
        # Load audio file
        audio = AudioSegment.from_wav(wav_path)
        segment_audio = audio[start_time * 1000:end_time * 1000]
        segment_filename = f"segment_{i}.wav"
        segment_path = os.path.join(output_dir, segment_filename)

        # Save segmented audio
        segment_audio.export(segment_path, format="wav")

        # Save corresponding transcription
        transcription_filename = segment_filename.replace('.wav', '.txt')
        transcription_path = os.path.join(output_dir, transcription_filename)
        with open(transcription_path, 'w') as f:
            f.write(transcript)

        logging.info(f'Saved segment: {segment_path} with transcription: {transcription_path}')

if __name__ == '__main__':
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    read_and_prepare_data(data_dir, output_dir, num_segments=20)
    logging.info("Dataset preparation complete.")
