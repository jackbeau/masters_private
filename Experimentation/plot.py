import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

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

def process_csv(file_name, data_type):
    # Load the data from the CSV file using NumPy
    data = np.genfromtxt(file_name, delimiter=',', dtype=None, encoding=None, names=True)
    
    # Extract columns for ease of use
    methods = data['method']
    page_numbers = data['page_number']
    y_coordinates = data['y_coordinate']
    chunk_indices = data['chunk_index']
    similarity_scores = data['similarity_score']
    
    # Get unique methods
    unique_methods = np.unique(methods)
    
    # Calculate metrics for similarity scores by method
    metrics = defaultdict(dict)
    for method in unique_methods:
        mask = methods == method
        scores = similarity_scores[mask]
        metrics[method]['mean'] = np.mean(scores)
        metrics[method]['std'] = np.std(scores)
    
    # Display metrics
    print(f"Metrics for {data_type}:")
    for method in unique_methods:
        print(f"Method: {method}, Mean: {metrics[method]['mean']:.2f}, Std: {metrics[method]['std']:.2f}")
    
    # Plotting similarity scores by method using violin plot
    plt.figure(figsize=(12, 8))
    sns.violinplot(x=methods, y=similarity_scores)
    plt.title('')
    plt.xlabel(r'\textbf{Approximate String Matching Scorer}', labelpad=14)
    plt.ylabel(r'\textbf{Similarity Score}', labelpad=14)
    plt.xticks(ticks=range(len(unique_methods)), labels=[wrap_labels(m.replace('_', ' ').title(), 14) for m in unique_methods])
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'Similarity_Scores_by_Method_for_{data_type}.png')
    plt.show()
    
    # Scatter plot to show the similarity scores on different pages
    plt.figure(figsize=(12, 8))
    for method in unique_methods:
        mask = methods == method
        sns.scatterplot(x=page_numbers[mask], y=similarity_scores[mask], label=method.replace('_', ' ').title(), alpha=0.6)
    
    plt.title(f'Similarity Scores by Page Number for {data_type}')
    plt.xlabel('Page Number')
    plt.ylabel('Similarity Score')
    plt.legend(title='Method', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'Similarity_Scores_by_Page_Number_for_{data_type}.png')
    plt.show()
    
    # Line plot to show chunk index progression over time
    plt.figure(figsize=(12, 8))
    for method in unique_methods:
        mask = methods == method
        sns.lineplot(x=np.arange(len(chunk_indices[mask])), y=chunk_indices[mask], label=method.replace('_', ' ').title(), alpha=0.6)
    
    plt.title(f'Chunk Index Progression by Page Number for {data_type}')
    plt.xlabel('Index')
    plt.ylabel('Chunk Index')
    plt.legend(title='Method', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'Chunk_Index_Progression_by_Page_Number_for_{data_type}.png')
    plt.show()

# Dictionary of file names and their types
files_and_types = {
    'compare_fuzzy methods.csv': 'Show Read-Through',
    'noise.csv': 'Noise',
    'recording.csv': 'Show Recording',
    'skipped.csv': 'Show Read-Through with Skipped Section'
}

# Process each file
for file_name, data_type in files_and_types.items():
    process_csv(file_name, data_type)
