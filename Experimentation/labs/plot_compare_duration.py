import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pydub import AudioSegment

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

def get_audio_duration(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    return len(audio) / 1000.0  # duration in seconds

def calculate_audio_lengths(data_dir):
    audio_lengths = {}
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.wav'):
                audio_path = os.path.join(root, file)
                duration = get_audio_duration(audio_path)
                audio_lengths[file] = duration
    return audio_lengths

def calculate_statistics(results_df):
    statistics = results_df.groupby('model').agg(
        average_latency=('latency', 'mean'),
        std_latency=('latency', 'std'),
        average_wer=('wer', 'mean'),
        std_wer=('wer', 'std')
    ).reset_index()

    return statistics

def generate_plots(results_df, audio_lengths):
    # Convert latency to float
    results_df['latency'] = results_df['latency'].astype(float)

    # Filter out rows with invalid audio paths and large models
    large_models = ['faster_whisper_large', 'whisper_large', 'faster_distil_whisper_largev2', 'faster_distil_whisper_largev3']
    results_df = results_df[
        results_df['audio_path'].notna() &
        results_df['audio_path'].apply(lambda x: isinstance(x, str)) &
        ~results_df['model'].isin(large_models)
    ]

    # Remove points with latency over 30 seconds
    results_df = results_df[results_df['latency'] <= 30]

    # Map audio file names to their lengths
    results_df['audio_length'] = results_df['audio_path'].apply(lambda x: audio_lengths.get(os.path.basename(x), np.nan))

    # Plot Latency vs. Audio Length
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=results_df, x='audio_length', y='latency', hue='model', style='model', palette='tab10')
    plt.xlabel('Audio Length (seconds)')
    plt.ylabel('Latency (seconds)')
    plt.title('Latency vs. Audio Length by Model')
    plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'latency_vs_audio_length.png'))
    plt.show()

    # Plot WER vs. Audio Length
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=results_df, x='audio_length', y='wer', hue='model', style='model', palette='tab10')
    plt.xlabel('Audio Length (seconds)')
    plt.ylabel('Word Error Rate (WER)')
    plt.title('WER vs. Audio Length by Model')
    plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'wer_vs_audio_length.png'))
    plt.show()

def main():
    results_df = load_results(results_dir)
    audio_lengths = calculate_audio_lengths(data_dir)
    statistics_df = calculate_statistics(results_df)

    # Add overall statistics to the dataframe
    overall_stats = pd.DataFrame({
        'model': ['Overall'],
        'average_latency': [statistics_df['average_latency'].mean()],
        'std_latency': [statistics_df['std_latency'].mean()],
        'average_wer': [statistics_df['average_wer'].mean()],
        'std_wer': [statistics_df['std_wer'].mean()],
        'average_audio_length': [np.mean(list(audio_lengths.values()))],
        'shortest_audio_length': [np.min(list(audio_lengths.values()))],
        'longest_audio_length': [np.max(list(audio_lengths.values()))]
    })

    statistics_df = pd.concat([statistics_df, overall_stats], ignore_index=True)

    # Save statistics to CSV
    output_file = os.path.join(results_dir, 'transcription_statistics.csv')
    statistics_df.to_csv(output_file, index=False)

    print(f'Statistics saved to {output_file}')

    # Generate plots
    generate_plots(results_df, audio_lengths)

if __name__ == '__main__':
    main()
