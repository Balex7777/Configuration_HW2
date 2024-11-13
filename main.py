import argparse
import subprocess
import os


def get_commit_dependencies(repo_path, file_hash):
    cmd = ["git", "log", "--pretty=format:%H %P", "--", file_hash]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    print(repo_path)
    dependencies = {}
    for line in result.stdout.splitlines():
        commit, *parents = line.split()
        dependencies[commit] = parents
    print(dependencies)
    return dependencies


def generate_puml(dependencies, output_file):
    with open(output_file, 'w') as f:
        f.write("@startuml\n")
        for commit, parents in dependencies.items():
            for parent in parents:
                f.write(f'"{parent}" --> "{commit}"\n')
        f.write("@enduml\n")


def run_plantuml(plantuml_path, puml_file):
    subprocess.run(["java", "-jar", plantuml_path, puml_file])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize git commit dependencies.")
    parser.add_argument("--graph-visualizer-path", required=True, help="Path to the PlantUML executable.")
    parser.add_argument("--repo-path", required=True, help="Path to the git repository.")
    parser.add_argument("--file-hash", required=True, help="File hash to filter commits by.")
    args = parser.parse_args()

    dependencies = get_commit_dependencies(args.repo_path, args.file_hash)
    puml_file = "dependency_graph.puml"
    generate_puml(dependencies, puml_file)
    run_plantuml(args.graph_visualizer_path, puml_file)
