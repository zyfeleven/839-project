import os
import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Define the project name and the path to the project tree JSON file
projects = ["scikit-learn-main", "autogluon-master", 'doccano-master']  # Replace with your actual project name
models = ["gpt-3.5", 'gpt-4o-mini']


class TreeNode:
    def __init__(self, name, path, is_dir=False):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.children = []
        self.code_elements = []  # List of code elements (classes, functions)
        self.code = ""  # Entire code of the file
        self.summary = ""  # Summary of the file
        self.code_element_summaries = []  # Summaries of each code element

    def add_child(self, node):
        self.children.append(node)

    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
            'is_dir': self.is_dir,
            'code_elements': self.code_elements,
            'code': self.code,
            'summary': self.summary,
            'code_element_summaries': self.code_element_summaries,
            'children': [child.to_dict() for child in self.children],
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data['name'], data['path'], data['is_dir'])
        node.code_elements = data.get('code_elements', [])
        node.code = data.get('code', "")
        node.summary = data.get('summary', "")
        node.code_element_summaries = data.get('code_element_summaries', [])
        node.children = [TreeNode.from_dict(child) for child in data.get('children', [])]
        return node

def load_tree_from_json(json_load_path):
    with open(json_load_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return TreeNode.from_dict(data)

def collect_summaries(root_node):
    """
    Traverse the tree and collect summaries and paths of all nodes,
    ignoring nodes named '__init__.py'.
    Returns a list of (node, summary) tuples and a list of paths.
    """
    summaries = []
    paths = []

    def traverse(node):
        # Skip nodes named '__init__.py'
        if node.name == "__init__.py":
            return
        if node.summary and not node.is_dir:
            summaries.append((node, node.summary))
            paths.append(node.path)
        for child in node.children:
            traverse(child)

    traverse(root_node)
    return summaries, paths

def main():
    for project_name in projects:
        for MODEL_NAME in models:
            json_load_path = f'./summaries/{project_name}_summary_{MODEL_NAME}.json'
            # Load the project tree from JSON
            root_node = load_tree_from_json(json_load_path)

            # Collect all summaries and paths
            node_summaries, paths = collect_summaries(root_node)
            summaries = [summary for node, summary in node_summaries]

            # Load a SentenceTransformer model (SciBERT)
            model_name = 'sentence-transformers/all-mpnet-base-v2'
            model = SentenceTransformer(model_name)

            # Encode summaries in batches for efficiency
            batch_size = 16
            embeddings_list = []
            for i in range(0, len(summaries), batch_size):
                batch_summaries = summaries[i:i+batch_size]
                # Encode directly with SentenceTransformer
                batch_embeddings = model.encode(batch_summaries, convert_to_tensor=True)
                embeddings_list.append(batch_embeddings)

            # Concatenate all embeddings
            embeddings = torch.cat(embeddings_list, dim=0)  # Shape: (num_summaries, embedding_dim)

            # Convert embeddings to numpy array
            embeddings_np = embeddings.cpu().numpy()

            # Compute cosine similarity matrix
            similarity_matrix = cosine_similarity(embeddings_np)

            # Save the similarity matrix to a file
            output_matrix_path = f'./similarity_matrices/{project_name}_{MODEL_NAME}_similarity_matrix.npy'
            os.makedirs(os.path.dirname(output_matrix_path), exist_ok=True)
            np.save(output_matrix_path, similarity_matrix)

            # Save the paths to a separate JSON file
            output_paths_path = f'./similarity_matrices/{project_name}_{MODEL_NAME}_paths.json'
            with open(output_paths_path, 'w', encoding='utf-8') as f:
                json.dump(paths, f, ensure_ascii=False, indent=4)

            print(f"Similarity matrix saved to {output_matrix_path}")
            print(f"Node paths saved to {output_paths_path}")

if __name__ == "__main__":
    main()
