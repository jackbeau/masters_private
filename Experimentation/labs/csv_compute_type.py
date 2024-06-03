import os
import pandas as pd

# Directory where results are stored
results_dir = 'labs/results/faster_whisper_base'
summary_file = 'labs/results/faster_whisper_base/summary_statistics_compute_type.csv'

def load_results(results_dir):
    all_results = []
    for file in os.listdir(results_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(results_dir, file)
            model_results = pd.read_csv(file_path)
            all_results.append(model_results)
    combined_results = pd.concat(all_results, ignore_index=True)
    return combined_results

def calculate_statistics(results_df):
    # Convert latency to float
    results_df['latency'] = results_df['latency'].astype(float)

    # Group by model and calculate mean and standard deviation
    statistics = results_df.groupby('model').agg({
        'latency': ['mean', 'std'],
        'wer': ['mean', 'std']
    }).reset_index()

    # Flatten the multi-level columns
    statistics.columns = ['model', 'latency_mean', 'latency_std', 'wer_mean', 'wer_std']

    return statistics

def save_statistics_to_csv(statistics, summary_file):
    statistics.to_csv(summary_file, index=False)
    print(f'Statistics saved to {summary_file}')

def main():
    results_df = load_results(results_dir)
    statistics = calculate_statistics(results_df)
    save_statistics_to_csv(statistics, summary_file)

if __name__ == '__main__':
    main()
