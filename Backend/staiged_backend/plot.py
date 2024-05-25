import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Function to process a single CSV and generate plots
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
    
    # Plotting similarity scores by method
    plt.figure(figsize=(12, 6))
    method_groups = [similarity_scores[methods == method] for method in unique_methods]
    plt.boxplot(method_groups, labels=unique_methods)
    plt.title(f'Similarity Scores by Method for {data_type}')
    plt.xlabel('Method')
    plt.ylabel('Similarity Score')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'Similarity_Scores_by_Method_for_{data_type}.png')
    plt.show()
    
    # Scatter plot to show the similarity scores on different pages
    plt.figure(figsize=(12, 6))
    for method in unique_methods:
        mask = methods == method
        plt.scatter(page_numbers[mask], similarity_scores[mask], label=method, alpha=0.6)
    
    plt.title(f'Similarity Scores by Page Number for {data_type}')
    plt.xlabel('Page Number')
    plt.ylabel('Similarity Score')
    plt.legend(title='Method', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'Similarity_Scores_by_Page_Number_for_{data_type}.png')
    plt.show()
    
    # Line plot to show chunk index progression over time
    plt.figure(figsize=(12, 6))
    for method in unique_methods:
        mask = methods == method
        plt.plot(np.arange(len(chunk_indices[mask])), chunk_indices[mask], label=method, alpha=0.6)
    
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
    'noise.csv': 'Noise',
    'recording.csv': 'Show Recording',
    'skipped.csv': 'Show Read-through with skipped section',
    'compare_fuzzy methods.csv': 'Show Read-through'
}

# Process each file
for file_name, data_type in files_and_types.items():
    process_csv(file_name, data_type)
