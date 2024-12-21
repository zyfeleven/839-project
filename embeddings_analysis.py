import os
import numpy as np
import json
import csv

project_name = "scikit-learn-main"
model_name = "gpt-3.5"
threshold = 0.9

# Prefix to remove
prefix_to_remove = "C:\\Users\\Yifan\\Desktop\\839\\839-project\\dataset"

# Paths to the saved files
matrix_path = f'./similarity_matrices/{project_name}_{model_name}_similarity_matrix.npy'
paths_path = f'./similarity_matrices/{project_name}_{model_name}_paths.json'
project_tree_path = f'./summaries/{project_name}_summary_{model_name}.json'

# Load the similarity matrix
similarity_matrix = np.load(matrix_path)
np.fill_diagonal(similarity_matrix, 0)

# Load the node paths
with open(paths_path, 'r', encoding='utf-8') as f:
    paths = json.load(f)

# Load the project tree
with open(project_tree_path, 'r', encoding='utf-8') as f:
    project_tree = json.load(f)


def build_summary_map(node, summary_map):
    """
    Recursively traverse the project tree to build a map from file path to summary.
    Uses the 'summary' field if present; otherwise defaults to 'No Summary Found'.
    """
    if not node['is_dir']:
        summary = node.get('summary', '').strip()
        if not summary:
            summary = "No Summary Found"
        summary_map[node['path']] = summary
    else:
        for child in node.get('children', []):
            build_summary_map(child, summary_map)


summary_map = {}
build_summary_map(project_tree, summary_map)

# Find pairs of nodes that exceed the threshold
indices = np.argwhere(similarity_matrix > threshold)

# CSV file to store the results
output_csv = f'./similarity_analysis/{project_name}_{model_name}_pairs_over_{threshold}.csv'

with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Write header: including paths, summaries, and similarity score
    writer.writerow(['node1_path', 'node1_summary', 'node2_path', 'node2_summary', 'similarity'])

    for i, j in indices:
        if i < j:  # Ensure each pair is counted only once
            path_i_original = paths[i]
            path_j_original = paths[j]

            # Extract file names
            file_name_i = os.path.basename(path_i_original)
            file_name_j = os.path.basename(path_j_original)

            # Skip if filenames are identical
            # if file_name_i == file_name_j:
            #     continue

            # Remove prefix from paths for display
            path_i = path_i_original.replace(prefix_to_remove, '')
            path_j = path_j_original.replace(prefix_to_remove, '')

            summary_i = summary_map.get(path_i_original, "No Summary Found")
            summary_j = summary_map.get(path_j_original, "No Summary Found")

            sim_score = similarity_matrix[i, j]

            # Write the pair information to the CSV
            writer.writerow([path_i, summary_i, path_j, summary_j, f"{sim_score:.4f}"])

print(f"Pairs exceeding threshold {threshold} have been written to {output_csv}.")
