import os
import json
import openai
from collections import deque

# Set your OpenAI API key
openai.api_key = ''  # Replace with your actual API key

projects = ['autogluon-master']

# Token limits for OpenAI models
MAX_TOKENS = 4096  # Total token limit for gpt-3.5
MAX_INPUT_TOKENS = 3096  # Reserve 1000 tokens for the response and overhead
MODEL_NAME = "gpt-3.5-turbo"  # Model to use

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

def save_tree_to_json(tree_node, json_save_path):
    os.makedirs(os.path.dirname(json_save_path), exist_ok=True)  # Ensure the directory exists
    with open(json_save_path, 'w', encoding='utf-8') as file:
        json.dump(tree_node.to_dict(), file, ensure_ascii=False, indent=4)

def estimate_tokens(text):
    # Simple estimation: assume 4 characters per token
    return len(text) // 4

def summarize_text(text, example_prompt):
    """
    Summarize the given text using the OpenAI API, limiting the summary to a single sentence.
    Returns the summary as a string.
    """
    # Prepare the prompt
    prompt = f"""{example_prompt}
Following the example above, please write a one-sentence summary for the following content:

Content:
{text}

Summary:
"""

    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,  # Reserve tokens for the response
            temperature=0.5,
            n=1,
            stop=None,
        )
        summary = response.choices[0].message['content'].strip()
        return summary
    except Exception as e:
        print(f"Error during summarization API call: {e}")
        return ""

def traverse_tree_and_summarize(root_node, project):
    """
    Traverse the tree from bottom to top, level by level, and generate summaries for each node.
    Summarize one file at a time, skipping files named '__init__.py'.
    """
    # Example prompt for one-shot prompting
    example_prompt = """Example:
Content:
class ExportedBoundingBox(BoundingBox):
    def to_dict(self):
        return {
            "uuid": str(self.uuid),
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "label": self.label.text,
        }

    def to_tuple(self):
        return self.x, self.y, self.width, self.height

    class Meta:
        proxy = True

Summary:
Class ExportedBoundingBox: A proxy model of BoundingBox that represents bounding box annotations in dictionary and tuple forms."""

    # Collect nodes at each level
    levels = {}
    max_level = 0

    queue = deque()
    queue.append((root_node, 0))

    while queue:
        node, level = queue.popleft()

        if level not in levels:
            levels[level] = []
        levels[level].append(node)
        max_level = max(max_level, level)

        for child in node.children:
            queue.append((child, level + 1))

    # Process levels from bottom to top
    for level in reversed(range(max_level + 1)):
        nodes = levels[level]

        for node in nodes:
            if node.is_dir:
                # Summarize children's summaries
                children_summaries = [child.summary for child in node.children if child.summary]
                content = "\n".join(children_summaries)
                if content:
                    content_tokens = estimate_tokens(content)
                    if content_tokens > MAX_INPUT_TOKENS:
                        print(f"Content too long to summarize for directory: {node.name}")
                        continue
                    print(f"Summarizing directory: {node.name}")
                    node.summary = summarize_text(content, example_prompt)
            else:
                # Skip files named '__init__.py'
                if node.name == '__init__.py':
                    print(f"Skipping file: {node.name}")
                    continue

                if node.code_elements:
                    print(f"Summarizing code elements in file: {node.name}")
                    code_elements = node.code_elements
                    code_element_summaries = []

                    for code_element in code_elements:
                        ce_tokens = estimate_tokens(code_element)
                        if ce_tokens > MAX_INPUT_TOKENS:
                            print(f"Code element too long to summarize in file: {node.name}")
                            continue
                        summary = summarize_text(code_element, example_prompt)
                        code_element_summaries.append(summary)

                    node.code_element_summaries = code_element_summaries

                    # Use code element summaries to create file summary
                    content = "\n".join(code_element_summaries)
                    content_tokens = estimate_tokens(content)
                    if content_tokens > MAX_INPUT_TOKENS:
                        print(f"Content too long to summarize for file: {node.name}")
                        continue
                    print(f"Summarizing file based on code element summaries: {node.name}")
                    node.summary = summarize_text(content, example_prompt)
                else:
                    # Summarize the whole file if no code elements
                    content = node.code
                    content_tokens = estimate_tokens(content)
                    if content_tokens > MAX_INPUT_TOKENS:
                        print(f"Content too long to summarize for file: {node.name}")
                        continue
                    print(f"Summarizing entire file: {node.name}")
                    node.summary = summarize_text(content, example_prompt)

        # For testing: exit after processing one level
        print("Summaries after processing one level:")
        for n in nodes:
            if n.summary:
                print(f"Node: {n.name}, Summary: {n.summary}")
        # Save the summaries to the JSON file before exiting
        json_save_path = f'./summaries/{project}_summary_{MODEL_NAME}.json'
        save_tree_to_json(root_node, json_save_path)
        print(f"Summaries saved to {json_save_path}")

    print("Summarization complete.")

def main():
    # Load the project tree from JSON
    for project in projects:
        json_load_path = f'./project_tree/{project}.json'
        if not os.path.exists(json_load_path):
            print(f"JSON file not found at {json_load_path}")
            return
        root_node = load_tree_from_json(json_load_path)

        # Traverse the tree and generate summaries
        traverse_tree_and_summarize(root_node, project)

        # Save the updated tree back to a new JSON file with summaries
        json_save_path = f'./summaries/{project}_summary_{MODEL_NAME}.json'
        save_tree_to_json(root_node, json_save_path)
        print(f"Summaries saved to {json_save_path}")

if __name__ == "__main__":
    main()
