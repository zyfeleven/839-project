import os

def count_code_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        # Exclude empty lines and comment lines
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        return len(code_lines)

def calculate_average_code_lines(project_path):
    total_lines = 0
    file_count = 0

    for root, dirs, files in os.walk(project_path):
        for file in files:
            # Adjust the extension based on the programming language
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                lines = count_code_lines(file_path)
                total_lines += lines
                file_count += 1

    if file_count == 0:
        return 0
    else:
        return total_lines / file_count

def main():
    projects = ['autogluon-master', 'scikit-learn-main', 'doccano-master']

    for project in projects:
        project_path = os.path.join('./dataset/', project)
        if not os.path.exists(project_path):
            print(f"Project directory '{project}' does not exist.")
            continue

        average_lines = calculate_average_code_lines(project_path)
        print(f"Average code lines per file in project '{project}': {average_lines:.2f}")

if __name__ == "__main__":
    main()
