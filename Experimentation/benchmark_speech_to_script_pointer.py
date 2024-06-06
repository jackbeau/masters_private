import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Matplotlib to use LaTeX for text rendering
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.size": 18,
    "axes.titlesize": 18,
    "axes.labelsize": 18,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 18,
    "figure.titlesize": 18,
    "text.latex.preamble": r"\usepackage{amsmath}"
})

# Simulated data for human participants with more realistic values and outliers
np.random.seed(42)
human_detection_time = np.random.normal(loc=2.5, scale=0.5, size=20).tolist()
human_detection_time += [5, 6]  # Adding outliers

human_relocation_time = np.random.normal(loc=45, scale=15, size=20).tolist()
human_relocation_time += [90, 100]  # Adding outliers
human_relocation_time = np.clip(human_relocation_time, 10, 120)  # Clipping to realistic range

human_accuracy = np.random.normal(loc=0.9, scale=0.05, size=20).tolist()
human_accuracy += [0.7, 0.75]  # Adding outliers
human_accuracy = np.clip(human_accuracy, 0.6, 1.0)  # Clipping to realistic range

# Simulated data for algorithm with more realistic values and outliers
algorithm_detection_time = np.random.normal(loc=9, scale=0.5, size=20).tolist()
algorithm_detection_time += [11, 12]  # Adding outliers

algorithm_relocation_time = np.random.normal(loc=2.75, scale=0.75, size=20).tolist()
algorithm_relocation_time += [5, 6]  # Adding outliers
algorithm_relocation_time = np.clip(algorithm_relocation_time, 1.5, 10)  # Clipping to realistic range

algorithm_accuracy = np.random.normal(loc=0.95, scale=0.02, size=20).tolist()
algorithm_accuracy += [0.85, 0.88]  # Adding outliers
algorithm_accuracy = np.clip(algorithm_accuracy, 0.8, 1.0)  # Clipping to realistic range

# Creating a DataFrame
data = {
    "Human Detection Time": human_detection_time,
    "Human Relocation Time": human_relocation_time,
    "Human Accuracy": human_accuracy,
    "Algorithm Detection Time": algorithm_detection_time,
    "Algorithm Relocation Time": algorithm_relocation_time,
    "Algorithm Accuracy": algorithm_accuracy
}
df_updated = pd.DataFrame(data)

# Define common bin edges
detection_bin_edges = np.histogram_bin_edges(df_updated[['Human Detection Time', 'Algorithm Detection Time']].values.ravel(), bins=15)
relocation_bin_edges = np.histogram_bin_edges(df_updated[['Human Relocation Time', 'Algorithm Relocation Time']].values.ravel(), bins=15)
accuracy_bin_edges = np.histogram_bin_edges(df_updated[['Human Accuracy', 'Algorithm Accuracy']].values.ravel(), bins=15)

# Detection Time Comparison
plt.figure(figsize=(12, 8))
sns.histplot(df_updated, x="Human Detection Time", kde=False, color='b', label='Human', bins=detection_bin_edges)
sns.histplot(df_updated, x="Algorithm Detection Time", kde=False, color='r', label='Algorithm', bins=detection_bin_edges)
# plt.title('Detection Time Comparison')
plt.title('')
plt.xlabel(r'\textbf{Time (seconds)}')
plt.ylabel(r'\textbf{Frequency}')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('detection_time_comparison.png')
plt.show()

# Relocation Time Comparison
plt.figure(figsize=(12, 8))
sns.histplot(df_updated, x="Human Relocation Time", kde=False, color='b', label='Human', bins=relocation_bin_edges)
sns.histplot(df_updated, x="Algorithm Relocation Time", kde=False, color='r', label='Algorithm', bins=relocation_bin_edges)
# plt.title('Successful Relocation Time Comparison')
plt.title('')
plt.xlabel(r'\textbf{Time (seconds)}')
plt.ylabel(r'\textbf{Frequency}') 
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('relocation_time_comparison.png')
plt.show()

# Accuracy Comparison
plt.figure(figsize=(12, 8))
sns.histplot(df_updated, x="Human Accuracy", kde=False, color='b', label='Human', bins=accuracy_bin_edges)
sns.histplot(df_updated, x="Algorithm Accuracy", kde=False, color='r', label='Algorithm', bins=accuracy_bin_edges)
# plt.title('Accuracy Comparison')
plt.title('')
plt.xlabel('Accuracy Rate')
plt.ylabel('Frequency')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('accuracy_comparison.png')
plt.show()
