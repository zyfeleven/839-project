import os
import json
import ast
from collections import deque

project_name = "scikit-learn-main"


class TreeNode:
    def __init__(self, name, path, is_dir=False):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.children = []
        self.code_elements = []  # New attribute to store code elements
        self.code = ""  # New attribute to store the entire code

    def add_child(self, node):
        self.children.append(node)

    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
            'is_dir': self.is_dir,
            'code_elements': self.code_elements,
            'code': self.code,
            'children': [child.to_dict() for child in self.children],
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data['name'], data['path'], data['is_dir'])
        node.code_elements = data.get('code_elements', [])
        node.code = data.get('code', "")
        node.children = [TreeNode.from_dict(child) for child in data.get('children', [])]
        return node


def load_tree_from_json(json_load_path):
    with open(json_load_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return TreeNode.from_dict(data)


def save_tree_to_json(tree_node, json_save_path):
    with open(json_save_path, 'w', encoding='utf-8') as file:
        json.dump(tree_node.to_dict(), file, ensure_ascii=False, indent=4)


def extract_code_elements(file_path):
    """
    Uses the ast module to parse the Python file and extract code elements,
    including functions and classes.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        elements = []

        class CodeElementVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Handle function definitions
                start_line = node.lineno
                end_line = node.end_lineno
                code_snippet = "\n".join(source.splitlines()[start_line - 1:end_line])
                docstring = ast.get_docstring(node)
                info = f"Function `{node.name}`"
                if docstring:
                    info += f": {docstring.strip().splitlines()[0]}"
                info += f"\nCode:\n{code_snippet}"
                elements.append(info)
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                # Handle class definitions
                start_line = node.lineno
                end_line = node.end_lineno
                code_snippet = "\n".join(source.splitlines()[start_line - 1:end_line])
                docstring = ast.get_docstring(node)
                info = f"Class `{node.name}`"
                if docstring:
                    info += f": {docstring.strip().splitlines()[0]}"
                info += f"\nCode:\n{code_snippet}"
                elements.append(info)
                self.generic_visit(node)

        visitor = CodeElementVisitor()
        visitor.visit(tree)

        return elements, source
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return [], ""


def traverse_tree_bottom_up(root_node):
    """
    Traverse the tree from bottom to top, level by level, and store code elements for each file.
    """
    levels = {}  # Dictionary mapping level number to list of nodes at that level
    max_level = 0  # Keep track of maximum level

    queue = deque()
    queue.append((root_node, 0))

    while queue:
        node, level = queue.popleft()

        if level in levels:
            levels[level].append(node)
        else:
            levels[level] = [node]

        max_level = max(max_level, level)

        for child in node.children:
            queue.append((child, level + 1))

    # Process levels from bottom to top
    for level in reversed(range(max_level + 1)):
        nodes = levels[level]
        for node in nodes:
            if not node.is_dir:
                # Extract code elements and entire code
                elements, code = extract_code_elements(node.path)
                node.code_elements = elements
                node.code = code
            else:
                continue  # Directories do not contain code elements


def main():
    # Load the project tree from JSON
    json_load_path = f'./project_tree/{project_name}.json'  # Adjust the path and filename as needed
    if not os.path.exists(json_load_path):
        print(f"JSON file not found at {json_load_path}")
        return
    root_node = load_tree_from_json(json_load_path)

    # Traverse the tree from bottom to top, level by level
    traverse_tree_bottom_up(root_node)

    # Save the updated tree back to JSON
    save_tree_to_json(root_node, json_load_path)
    print(f"Updated project tree saved to {json_load_path}")


if __name__ == "__main__":
    main()
