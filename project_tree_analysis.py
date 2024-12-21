import json
from radon.complexity import cc_visit


project_name = "scikit-learn-main"
def is_python_file(node):
    # A Python file likely ends with .py and is not a directory.
    return (not node['is_dir']) and node['name'].endswith('.py')

def analyze_file(node):
    """
    Analyzes a single file node to compute:
      - Cyclomatic complexity
      - Number of functions
      - Number of classes

    Returns: (avg_cc, num_functions, num_classes)
    """
    code = node.get('code', '')
    # Compute cyclomatic complexity of each function/block
    complexity_results = cc_visit(code)

    # Average complexity (per block) for the file
    if complexity_results:
        avg_cc = sum(res.complexity for res in complexity_results) / len(complexity_results)
    else:
        avg_cc = 0.0

    # Counting functions and classes:
    # We assume code_elements may contain strings like "Function `foo`" or "Class `Bar`".
    code_elements = node.get('code_elements', [])
    num_functions = sum('Function ' in elem for elem in code_elements)
    num_classes = sum('Class ' in elem for elem in code_elements)

    return avg_cc, num_functions, num_classes

def traverse_tree(node):
    """
    Recursively traverses the project tree and collects stats for each Python file.

    Returns: A list of dicts with keys: path, avg_cc, num_functions, num_classes
    """
    results = []
    if node['is_dir']:
        # Recurse into children
        for child in node.get('children', []):
            results.extend(traverse_tree(child))
    else:
        # Leaf node (file)
        if is_python_file(node):
            avg_cc, num_functions, num_classes = analyze_file(node)
            results.append({
                'path': node['path'],
                'avg_cc': avg_cc,
                'num_functions': num_functions,
                'num_classes': num_classes
            })
    return results

if __name__ == "__main__":
    # Load the project tree from a JSON file
    # Replace 'project_tree.json' with the actual path to your JSON file
    with open(f'./project_tree/{project_name}.json', 'r', encoding='utf-8') as f:
        project_tree = json.load(f)

    file_stats = traverse_tree(project_tree)

    # Compute overall averages
    if file_stats:
        avg_cc_overall = sum(d['avg_cc'] for d in file_stats) / len(file_stats)
        avg_functions_overall = sum(d['num_functions'] for d in file_stats) / len(file_stats)
        avg_classes_overall = sum(d['num_classes'] for d in file_stats) / len(file_stats)
    else:
        avg_cc_overall = 0.0
        avg_functions_overall = 0.0
        avg_classes_overall = 0.0

    print("Per-file Statistics:")
    for f in file_stats:
        print(f"File: {f['path']}, Avg CC: {f['avg_cc']:.2f}, Functions: {f['num_functions']}, Classes: {f['num_classes']}")

    print("\nOverall Averages:")
    print(f"Average Cyclomatic Complexity per File: {avg_cc_overall:.2f}")
    print(f"Average Number of Functions per File: {avg_functions_overall:.2f}")
    print(f"Average Number of Classes per File: {avg_classes_overall:.2f}")
