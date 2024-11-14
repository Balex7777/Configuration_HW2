import argparse
import subprocess
import os


def get_commit_dependencies(repo_path, file_hash):
    cmd = ["git", "log", "--pretty=format:%H %P", "--", file_hash]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    dependencies = {}
    commit_order = {}
    count = 1
    for line in result.stdout.splitlines():
        commit, *parents = line.split()
        dependencies[commit] = parents
        commit_order[commit] = count  # Сохраняем порядковый номер коммита
        count += 1
    return dependencies, commit_order


def generate_puml(dependencies, commit_order, output_file):
    with open(output_file, 'w') as f:
        f.write("@startuml\n")
        for commit, parents in dependencies.items():
            commit_label = f'{commit_order.get(commit, "0")}: {commit}'  # Используем 0 для отсутствующих номеров
            for parent in parents:
                parent_label = f'{commit_order.get(parent, "0")}: {parent}'
                f.write(f'"{parent_label}" --> "{commit_label}"\n')
        f.write("@enduml\n")


def run_plantuml(plantuml_path, puml_file):
    subprocess.run(["java", "-jar", plantuml_path, puml_file])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize git commit dependencies.")
    parser.add_argument("--graph-visualizer-path", required=True, help="Path to the PlantUML executable.")
    parser.add_argument("--repo-path", required=True, help="Path to the git repository.")
    parser.add_argument("--file-hash", required=True, help="File hash to filter commits by.")
    args = parser.parse_args()

    dependencies, commit_order = get_commit_dependencies(args.repo_path, args.file_hash)
    puml_file = "dependency_graph.puml"
    generate_puml(dependencies, commit_order, puml_file)
    run_plantuml(args.graph_visualizer_path, puml_file)
