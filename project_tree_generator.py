# project_tree_generator.py

import os
import json

# Define the root directory path here
file_path = r"C:\Users\Yifan\Desktop\839\839-project\dataset\autogluon-master"

class TreeNode:
    def __init__(self, name, path, is_dir=False):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
            'is_dir': self.is_dir,
            'children': [child.to_dict() for child in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data['name'], data['path'], data['is_dir'])
        node.children = [TreeNode.from_dict(child) for child in data.get('children', [])]
        return node

    def __repr__(self, level=0):
        indent = '  ' * level
        representation = f"{indent}{'📁' if self.is_dir else '📄'} {self.name}\n"
        for child in self.children:
            representation += child.__repr__(level + 1)
        return representation

def build_project_tree(root_path, delete_other_files=False):
    root_name = os.path.basename(root_path.rstrip(os.sep)) or root_path
    root_node = TreeNode(root_name, root_path, is_dir=True)
    stack = [(root_node, root_path)]

    while stack:
        current_node, current_path = stack.pop()
        try:
            for entry in os.listdir(current_path):
                entry_path = os.path.join(current_path, entry)
                if os.path.isdir(entry_path):
                    dir_node = TreeNode(entry, entry_path, is_dir=True)
                    current_node.add_child(dir_node)
                    stack.append((dir_node, entry_path))
                elif entry.endswith('.py'):
                    file_node = TreeNode(entry, entry_path, is_dir=False)
                    current_node.add_child(file_node)
                else:
                    if delete_other_files:
                        try:
                            os.remove(entry_path)
                            print(f"Deleted file: {entry_path}")
                        except Exception as e:
                            print(f"Error deleting file {entry_path}: {e}")
        except PermissionError as e:
            print(f"Permission denied: {e}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")

    return root_node

def save_tree_to_json(root_node):
    # Create the 'project_tree' directory if it doesn't exist
    save_directory = './project_tree'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Use the project name for the JSON file
    project_name = root_node.name
    json_save_path = os.path.join(save_directory, f"{project_name}.json")

    with open(json_save_path, 'w', encoding='utf-8') as file:
        json.dump(root_node.to_dict(), file, indent=2)

    print(f"Project tree saved to {json_save_path}")

def load_tree_from_json(json_load_path):
    with open(json_load_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return TreeNode.from_dict(data)

def main():
    root_directory = file_path
    if not os.path.exists(root_directory):
        print("The specified directory does not exist.")
        return

    print("\n⚠️ WARNING: This script will delete all files that are not .py or .ipynb files in the specified directory and its subdirectories.")
    # Uncomment the following lines to include a confirmation prompt
    # confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    # if confirm != 'yes':
    #     print("Operation cancelled.")
    #     return

    project_tree = build_project_tree(root_directory, delete_other_files=True)

    # Save the tree JSON file in the 'project_tree' directory
    save_tree_to_json(project_tree)

    print("\nProject Tree Structure (only .py and .ipynb files and folders):")
    print(project_tree)

    # Optionally, load the tree from JSON
    # Uncomment the following lines if you wish to load and display the tree from the saved JSON file
    # json_load_path = os.path.join('./project_tree', f"{project_tree.name}.json")
    # loaded_tree = load_tree_from_json(json_load_path)
    # print("\nLoaded Project Tree Structure:")
    # print(loaded_tree)

if __name__ == "__main__":
    main()
