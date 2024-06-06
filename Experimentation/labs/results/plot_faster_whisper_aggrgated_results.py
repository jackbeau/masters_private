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
    "font.size": 38,
    "axes.titlesize": 38,
    "axes.labelsize": 38,
    "xtick.labelsize": 38,
    "ytick.labelsize": 38,
    "legend.fontsize": 38,
    "figure.titlesize": 38,
    "text.latex.preamble": r"\usepackage{amsmath}"
})

def load_results(summary_file):
    return pd.read_csv(summary_file)

def generate_plot(data, x, y1, y2, x_label, y1_label, y2_label, filename):
    plt.figure(figsize=(14, 10))
    ax = sns.lineplot(data=data, x=x, y=y1, marker='o', label='Latency (seconds)', legend=False)
    ax.fill_between(data[x], data[y1] - data['latency_std'], data[y1] + data['latency_std'], alpha=0.2)
    ax.set_xlabel(x_label, labelpad=20)
    ax.set_ylabel(y1_label, labelpad=20)
    
    ax2 = ax.twinx()
    sns.lineplot(data=data, x=x, y=y2, marker='o', color='orange', label="WER", ax=ax2, legend=False)
    ax2.set_ylabel(y2_label, labelpad=20)

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=False, prop={'weight': 'normal'})
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, filename), bbox_inches='tight')
    plt.show()

def main():
    results_df = load_results(summary_file)
    
    # Filter data for plotting
    df_cpu = results_df[results_df['beam_size'] == 1]
    df_beam = results_df[results_df['cpu_threads'] == 4]
    
    # Generate plots with consistent sizes
    generate_plot(df_cpu, 'cpu_threads', 'latency_mean', 'wer_mean', 
                  r'\textbf{CPU Threads}', r'\textbf{Latency (seconds)}', r'\textbf{WER}', 
                  'latency_vs_cpu_threads.png')
    generate_plot(df_beam, 'beam_size', 'latency_mean', 'wer_mean', 
                  r'\textbf{Beam Size}', r'\textbf{Latency (seconds)}', r'\textbf{WER}', 
                  'latency_vs_beam_size.png')

if __name__ == '__main__':
    main()
