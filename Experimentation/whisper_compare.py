import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pydub import AudioSegment

# Directory where results are stored
results_dir = 'labs/results'
data_dir = 'labs/experiment_dataset'

# Configure Matplotlib to use LaTeX for text rendering
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.size": 16,
    "axes.titlesize": 16,
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 16,
    "figure.titlesize": 16,
    "text.latex.preamble": r"\usepackage{amsmath}"
})

def wrap_labels(label, width):
    """Wrap x-axis labels to new lines to fit within the specified width."""
    words = label.split()
    lines = []
    current_line = []

    for word in words:
        if sum(len(w) for w in current_line) + len(current_line) + len(word) <= width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    return "\n".join(lines)

def load_results(results_dir):
    all_results = []
    for file in os.listdir(results_dir):
        if file.endswith('.csv'):
            model_name = os.path.splitext(file)[0]
            print(f"Processing file: {file} with initial model name: {model_name}")
            if 'Transcription Statistics' in model_name:
                print(f"Skipping file: {file} as it matches 'Transcription Statistics'")
                continue
            model_name = model_name.replace('Transcription_Results_', '').replace('_', ' ').title().strip()
            print(f"Formatted model name: {model_name}")
            file_path = os.path.join(results_dir, file)
            model_results = pd.read_csv(file_path)
            model_results['model'] = model_name
            all_results.append(model_results)
    combined_results = pd.concat(all_results, ignore_index=True)
    print(f"Combined results: {combined_results['model'].unique()}")
    return combined_results

def get_audio_duration(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    return len(audio) / 1000.0  # duration in seconds

def calculate_audio_lengths(data_dir):
    audio_lengths = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.wav'):
                audio_path = os.path.join(root, file)
                duration = get_audio_duration(audio_path)
                audio_lengths.append(duration)
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

    # Filter out 'Transcription Statistics' from results_df if it exists
    results_df = results_df[results_df['model'] != 'Transcription Statistics']

    # Select numeric columns for plotting
    numeric_columns = ['latency', 'wer', 'mer', 'wil', 'wip', 'cer']

    # Calculate audio length metrics
    average_length = np.mean(audio_lengths)
    shortest_length = np.min(audio_lengths)
    longest_length = np.max(audio_lengths)

    # Group by model and calculate mean values for numeric metrics
    grouped_results = results_df.groupby('model')[numeric_columns].mean().reset_index()

    print(f"Models in plot: {grouped_results['model'].unique()}")

    # Get unique model names for x-axis labels
    unique_models = results_df['model'].unique()

    # Plot Box Plots for Latency with Audio Length Metrics
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='model', y='latency', data=results_df)
    plt.axhline(y=average_length, color='r', linestyle='--', label='Average Audio Length')
    plt.axhline(y=shortest_length, color='g', linestyle='--', label='Shortest Audio Length')
    plt.axhline(y=longest_length, color='b', linestyle='--', label='Longest Audio Length')
    plt.xlabel(r'\textbf{Model}')
    plt.ylabel(r'\textbf{Latency (seconds)}')
    plt.title('')
    plt.xticks(rotation=0, ticks=range(len(unique_models)), labels=[wrap_labels(m, 14) for m in unique_models])
    legend = plt.legend()
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(1)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'latency_boxplot_with_audio_lengths.png'))
    plt.show()

    # Plot Violin Plots for Latency with Audio Length Metrics
    plt.figure(figsize=(12, 8))
    sns.violinplot(x='model', y='latency', data=results_df)
    plt.axhline(y=average_length, color='r', linestyle='--', label='Average Audio Length')
    plt.axhline(y=shortest_length, color='g', linestyle='--', label='Shortest Audio Length')
    plt.axhline(y=longest_length, color='b', linestyle='--', label='Longest Audio Length')
    plt.xlabel(r'\textbf{Model}')
    plt.ylabel(r'\textbf{Latency (seconds)}')
    plt.title(r'Latency Distribution by Model with Audio Length Metrics')
    plt.xticks(rotation=0, ticks=range(len(unique_models)), labels=[wrap_labels(m, 14) for m in unique_models])
    legend = plt.legend()
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(1)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'latency_violinplot_with_audio_lengths.png'))
    plt.show()


def main():
    results_df = load_results(results_dir)
    audio_lengths = calculate_audio_lengths(data_dir)
    statistics_df = calculate_statistics(results_df)

    # Save statistics to CSV without adding overall statistics
    output_file = os.path.join(results_dir, 'transcription_statistics.csv')
    statistics_df.to_csv(output_file, index=False)

    print(f'Statistics saved to {output_file}')

    # Generate plots
    generate_plots(results_df, audio_lengths)

if __name__ == '__main__':
    main()
