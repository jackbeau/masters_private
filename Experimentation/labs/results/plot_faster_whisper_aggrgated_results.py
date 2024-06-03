import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Directory where results are stored
results_dir = 'labs/results/faster_whisper_base'
summary_file = 'labs/results/faster_whisper_base/transcription_aggregated_results.csv'

def load_results(summary_file):
    return pd.read_csv(summary_file)

def generate_plots(results_df):
    sns.set(style="whitegrid")

    # Filter data for plotting
    df_cpu = results_df[results_df['beam_size'] == 1]
    df_beam = results_df[results_df['cpu_threads'] == 4]

    # Plot Latency and WER vs. CPU Threads
    plt.figure(figsize=(14, 7))
    ax1 = plt.subplot(1, 2, 1)
    sns.lineplot(data=df_cpu, x='cpu_threads', y='latency_mean', marker='o', label='Latency', ax=ax1)
    ax1.fill_between(df_cpu['cpu_threads'], 
                     df_cpu['latency_mean'] - df_cpu['latency_std'], 
                     df_cpu['latency_mean'] + df_cpu['latency_std'], alpha=0.2)
    ax1.set_xlabel('CPU Threads')
    ax1.set_ylabel('Latency (seconds)')
    ax1.set_title('Latency vs. CPU Threads for faster_whisper base with a beam size of 1')
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    sns.lineplot(data=df_cpu, x='cpu_threads', y='wer_mean', marker='o', color='orange', label='WER', ax=ax2)
    ax2.fill_between(df_cpu['cpu_threads'], 
                     df_cpu['wer_mean'] - df_cpu['wer_std'], 
                     df_cpu['wer_mean'] + df_cpu['wer_std'], color='orange', alpha=0.2)
    ax2.set_ylabel('WER')
    ax2.legend(loc='upper right')

    # Plot Latency and WER vs. Beam Size
    plt.subplot(1, 2, 2)
    ax3 = sns.lineplot(data=df_beam, x='beam_size', y='latency_mean', marker='o', label='Latency')
    ax3.fill_between(df_beam['beam_size'], 
                     df_beam['latency_mean'] - df_beam['latency_std'], 
                     df_beam['latency_mean'] + df_beam['latency_std'], alpha=0.2)
    ax3.set_xlabel('Beam Size')
    ax3.set_ylabel('Latency (seconds)')
    ax3.set_title('Latency vs. Beam Size for faster_whisper base with a 4 threads')
    ax3.legend(loc='upper left')

    ax4 = ax3.twinx()
    sns.lineplot(data=df_beam, x='beam_size', y='wer_mean', marker='o', color='orange', label='WER', ax=ax4)
    ax4.fill_between(df_beam['beam_size'], 
                     df_beam['wer_mean'] - df_beam['wer_std'], 
                     df_beam['wer_mean'] + df_beam['wer_std'], color='orange', alpha=0.2)
    ax4.set_ylabel('WER')
    ax4.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'latency_and_wer_vs_cpu_threads_and_beam_size.png'))
    plt.show()

def main():
    results_df = load_results(summary_file)
    generate_plots(results_df)

if __name__ == '__main__':
    main()
