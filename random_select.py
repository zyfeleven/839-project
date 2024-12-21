import os
import json
import random

# Reuse your TreeNode class and related functions
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

def collect_file_nodes(node, file_nodes):
    if not node.is_dir:
        file_nodes.append(node)
    for child in node.children:
        collect_file_nodes(child, file_nodes)

def main():
    projects = ['autogluon-master', 'scikit-learn-main', 'doccano-master']
    MODEL_NAME = "gpt-3.5"  # Adjust if needed

    for project in projects:
        # Load the project tree with summaries
        json_load_path = f'./summaries/{project}_summary_{MODEL_NAME}.json'
        if not os.path.exists(json_load_path):
            print(f"JSON file not found at {json_load_path}")
            continue
        root_node = load_tree_from_json(json_load_path)
        file_nodes = []
        collect_file_nodes(root_node, file_nodes)

        if len(file_nodes) == 0:
            print(f"No files found in project {project}")
            continue

        # Determine number of files to select
        num_files_to_select = min(20, len(file_nodes))

        # File to store selected file paths
        selected_files_path = f'./random_selection/{project}_selected_files.json'
        os.makedirs(os.path.dirname(selected_files_path), exist_ok=True)

        if os.path.exists(selected_files_path):
            # Load previously selected files
            with open(selected_files_path, 'r', encoding='utf-8') as f:
                selected_file_paths = json.load(f)
            # Map paths to TreeNode objects
            path_to_node = {node.path: node for node in file_nodes}
            selected_files = [path_to_node[path] for path in selected_file_paths if path in path_to_node]
            print(f"Loaded previously selected files for project '{project}'.")
        else:
            # Randomly select files and save their paths
            selected_files = random.sample(file_nodes, num_files_to_select)
            selected_file_paths = [node.path for node in selected_files]
            with open(selected_files_path, 'w', encoding='utf-8') as f:
                json.dump(selected_file_paths, f, ensure_ascii=False, indent=4)
            print(f"Randomly selected files for project '{project}' and saved selection.")

        # Prepare the output content
        output_lines = []
        for idx, file_node in enumerate(selected_files, 1):
            output_lines.append(f"=== File {idx} ===")
            output_lines.append(f"Project Path: {file_node.path}")
            output_lines.append(f"File Name: {file_node.name}\n")
            output_lines.append("Code:")
            output_lines.append(file_node.code)
            output_lines.append("\nSummary:")
            output_lines.append(file_node.summary)
            output_lines.append("\nCode Element Summaries:")
            for ces in file_node.code_element_summaries:
                output_lines.append(f"- {ces}")
            output_lines.append("\n")  # Add an extra newline for readability

        # Save the output to a file
        output_content = "\n".join(output_lines)
        output_file_path = f'./random_selection/{project}_{MODEL_NAME}_random_selection.txt'
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(output_content)

        print(f"Selected files for project '{project}' have been saved to '{output_file_path}'")

if __name__ == "__main__":
    main()
