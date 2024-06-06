import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Matplotlib to use LaTeX for text rendering
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.size": 24,
    "axes.titlesize": 24,
    "axes.labelsize": 24,
    "xtick.labelsize": 24,
    "ytick.labelsize": 24,
    "legend.fontsize": 24,
    "figure.titlesize": 24,
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

def load_and_process_data(file_name, data_type):
    # Load the data from the CSV file using NumPy
    data = np.genfromtxt(file_name, delimiter=',', dtype=None, encoding=None, names=True)
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(data)
    
    # Add a column for the data type (test case)
    df['test_case'] = data_type
    
    return df

# Dictionary of file names and their types
files_and_types = {
    'noise.csv': 'Noise',
    'recording.csv': 'Show \nRecording',
    'skipped.csv': 'Show \nRead-Through\nWith Skipped\n Section',
    'compare_fuzzy methods.csv': 'Show \nRead-Through'
}

# Load and combine all data
all_data = pd.DataFrame()
for file_name, data_type in files_and_types.items():
    df = load_and_process_data(file_name, data_type)
    all_data = pd.concat([all_data, df], ignore_index=True)

# Calculate mean similarity score for each method and test case
heatmap_data = all_data.groupby(['test_case', 'method'])['similarity_score'].mean().unstack()

# Replace underscores and apply capitalization for better readability
heatmap_data.columns = [col.replace('_', ' ').title() for col in heatmap_data.columns]
heatmap_data.index = [idx.replace('_', ' ').title() for idx in heatmap_data.index]

# Create a heatmap with a single color and varying opacity
plt.figure(figsize=(16, 10))
sns.heatmap(heatmap_data, annot=True, cmap='Blues', fmt=".2f", linewidths=.5, cbar=False)
plt.title('')
plt.xlabel(r'\textbf{Approximate String Matching Scorer}', labelpad=14)
plt.ylabel(r'\textbf{Test Case}', labelpad=14)
plt.xticks(ticks=np.arange(len(heatmap_data.columns)) + 0.5, labels=[wrap_labels(col, 14) for col in heatmap_data.columns], rotation=0, ha='center')  # Apply wrapping, set x-axis labels to horizontal and centered
plt.yticks(rotation=0)  # Set y-axis labels to be horizontal
plt.tight_layout()
plt.savefig('Mean_Similarity_Scores_Heatmap.png')
plt.show()
