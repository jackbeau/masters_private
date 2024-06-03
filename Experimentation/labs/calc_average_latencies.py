import os
import pandas as pd
import numpy as np

# Directory where results are stored
results_dir = 'labs/results'
data_dir = 'labs/experiment_dataset'

def load_results(results_dir):
    all_results = []
    for file in os.listdir(results_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(results_dir, file)
            model_results = pd.read_csv(file_path)
            all_results.append(model_results)
    combined_results = pd.concat(all_results, ignore_index=True)
    return combined_results

def calculate_audio_lengths(data_dir):
    audio_lengths = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.wav'):
                audio_path = os.path.join(root, file)
                duration = get_audio_duration(audio_path)
                audio_lengths.append(duration)
    return audio_lengths

def get_audio_duration(audio_path):
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(audio_path)
    return len(audio) / 1000.0  # duration in seconds

def calculate_statistics(results_df):
    statistics = results_df.groupby('model').agg(
        average_latency=('latency', 'mean'),
        std_latency=('latency', 'std'),
        average_wer=('wer', 'mean'),
        std_wer=('wer', 'std')
    ).reset_index()

    return statistics

def main():
    results_df = load_results(results_dir)
    statistics_df = calculate_statistics(results_df)

    # Calculate audio lengths
    audio_lengths = calculate_audio_lengths(data_dir)
    average_length = np.mean(audio_lengths)
    shortest_length = np.min(audio_lengths)
    longest_length = np.max(audio_lengths)

    # Add overall statistics to the dataframe
    overall_stats = pd.DataFrame({
        'model': ['Overall'],
        'average_latency': [statistics_df['average_latency'].mean()],
        'std_latency': [statistics_df['std_latency'].mean()],
        'average_wer': [statistics_df['average_wer'].mean()],
        'std_wer': [statistics_df['std_wer'].mean()],
        'average_audio_length': [average_length],
        'shortest_audio_length': [shortest_length],
        'longest_audio_length': [longest_length]
    })

    statistics_df = pd.concat([statistics_df, overall_stats], ignore_index=True)

    # Save statistics to CSV
    output_file = os.path.join(results_dir, 'transcription_statistics.csv')
    statistics_df.to_csv(output_file, index=False)

    print(f'Statistics saved to {output_file}')

if __name__ == '__main__':
    main()
