import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Directory where results are stored
results_dir = 'labs/results'

def load_results(results_dir):
    all_results = []
    for file in os.listdir(results_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(results_dir, file)
            model_results = pd.read_csv(file_path)
            all_results.append(model_results)
    combined_results = pd.concat(all_results, ignore_index=True)
    return combined_results

def generate_plots(results_df):
    # Convert latency to float
    results_df['latency'] = results_df['latency'].astype(float)

    # Select numeric columns for plotting
    numeric_columns = ['latency', 'wer', 'mer', 'wil', 'wip', 'cer']

    # Plot Box Plots
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='model', y='wer', data=results_df)
    plt.xlabel('Model')
    plt.ylabel('Word Error Rate (WER)')
    plt.title('Word Error Rate (WER) Distribution by Model')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'wer_boxplot.png'))
    plt.show()

    plt.figure(figsize=(12, 8))
    sns.boxplot(x='model', y='cer', data=results_df)
    plt.xlabel('Model')
    plt.ylabel('Character Error Rate (CER)')
    plt.title('Character Error Rate (CER) Distribution by Model')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'cer_boxplot.png'))
    plt.show()

    plt.figure(figsize=(12, 8))
    sns.boxplot(x='model', y='latency', data=results_df)
    plt.xlabel('Model')
    plt.ylabel('Latency (seconds)')
    plt.title('Latency Distribution by Model')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'latency_boxplot.png'))
    plt.show()

    # Plot Violin Plots
    plt.figure(figsize=(12, 8))
    sns.violinplot(x='model', y='wer', data=results_df)
    plt.xlabel('Model')
    plt.ylabel('Word Error Rate (WER)')
    plt.title('Word Error Rate (WER) Distribution by Model')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'wer_violinplot.png'))
    plt.show()

    plt.figure(figsize=(12, 8))
    sns.violinplot(x='model', y='cer', data=results_df)
    plt.xlabel('Model')
    plt.ylabel('Character Error Rate (CER)')
    plt.title('Character Error Rate (CER) Distribution by Model')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'cer_violinplot.png'))
    plt.show()

    plt.figure(figsize=(12, 8))
    sns.violinplot(x='model', y='latency', data=results_df)
    plt.xlabel('Model')
    plt.ylabel('Latency (seconds)')
    plt.title('Latency Distribution by Model')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'latency_violinplot.png'))
    plt.show()

    # Plot Heatmap for Correlation Matrix
    correlation_matrix = results_df[numeric_columns].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Matrix of Metrics')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'correlation_matrix.png'))
    plt.show()

def main():
    results_df = load_results(results_dir)
    generate_plots(results_df)

if __name__ == '__main__':
    main()
