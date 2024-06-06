import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Directory where results are stored
results_dir = 'labs/results/faster_whisper_base'
summary_file = 'labs/results/faster_whisper_base/transcription_aggregated_results.csv'

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

def load_results(summary_file):
    return pd.read_csv(summary_file)

def generate_latency_vs_cpu_threads_plot(df_cpu):
    plt.figure(figsize=(12, 8))
    ax1 = sns.lineplot(data=df_cpu, x='cpu_threads', y='latency_mean', marker='o', label='Latency')
    ax1.fill_between(df_cpu['cpu_threads'], 
                     df_cpu['latency_mean'] - df_cpu['latency_std'], 
                     df_cpu['latency_mean'] + df_cpu['latency_std'], alpha=0.2)
    ax1.set_xlabel(r'\textbf{CPU Threads}', labelpad=14)
    ax1.set_ylabel(r'\textbf{Latency (seconds)}', labelpad=14)
    # ax1.set_title(r'Latency vs. CPU Threads for Faster Whisper Base with a Beam Size of 1')
    ax1.set_title('')
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    sns.lineplot(data=df_cpu, x='cpu_threads', y='wer_mean', marker='o', color='orange', label='WER', ax=ax2)
    # ax2.fill_between(df_cpu['cpu_threads'], 
    #                  df_cpu['wer_mean'] - df_cpu['wer_std'], 
    #                  df_cpu['wer_mean'] + df_cpu['wer_std'], color='orange', alpha=0.2)
    ax2.set_ylabel(r'\textbf{WER}', labelpad=14)
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.savefig(os.path.join(results_dir, 'latency_vs_cpu_threads.png'))
    plt.show()

def generate_latency_vs_beam_size_plot(df_beam):
    plt.figure(figsize=(12, 8))
    ax3 = sns.lineplot(data=df_beam, x='beam_size', y='latency_mean', marker='o', label='Latency')
    ax3.fill_between(df_beam['beam_size'], 
                     df_beam['latency_mean'] - df_beam['latency_std'], 
                     df_beam['latency_mean'] + df_beam['latency_std'], alpha=0.2)
    ax3.set_xlabel(r'\textbf{Beam Size}', labelpad=14)
    ax3.set_ylabel(r'\textbf{Latency (seconds)}', labelpad=14)
    # ax3.set_title(r'Latency vs. Beam Size for Faster Whisper Base with 4 Threads')
    ax3.set_title('')
    ax3.legend(loc='upper left')

    ax4 = ax3.twinx()
    sns.lineplot(data=df_beam, x='beam_size', y='wer_mean', marker='o', color='orange', label='WER', ax=ax4)
    ax4.fill_between(df_beam['beam_size'], 
                     df_beam['wer_mean'] - df_beam['wer_std'], 
                     df_beam['wer_mean'] + df_beam['wer_std'], color='white', alpha=0)
    ax4.set_ylabel(r'\textbf{WER}', labelpad=14)
    ax4.legend(loc='upper right')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'latency_vs_beam_size.png'))
    plt.show()

def main():
    results_df = load_results(summary_file)
    
    # Filter data for plotting
    df_cpu = results_df[results_df['beam_size'] == 1]
    df_beam = results_df[results_df['cpu_threads'] == 4]
    
    # Generate plots
    generate_latency_vs_cpu_threads_plot(df_cpu)
    generate_latency_vs_beam_size_plot(df_beam)

if __name__ == '__main__':
    main()
