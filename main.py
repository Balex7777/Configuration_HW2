import argparse
import subprocess
import os
import json
import zlib


def parse_object(object_hash, description=None):
    object_path = os.path.join(config['repo_path'], '.git', 'objects', object_hash[:2], object_hash[2:])
    with open(object_path, 'rb') as file:
        raw_object_content = zlib.decompress(file.read())
        header, raw_object_body = raw_object_content.split(b'\x00', maxsplit=1)
        object_type, content_size = header.decode().split(' ')
        object_dict = {}

        if object_type == 'commit':
            object_dict['label'] = r'[commit]\n' + object_hash[:6]
            object_dict['children'] = parse_commit(raw_object_body)

        elif object_type == 'tree':
            object_dict['label'] = r'[tree]\n' + object_hash[:6]
            object_dict['children'] = parse_tree(raw_object_body)

        elif object_type == 'blob':
            object_dict['label'] = r'[blob]\n' + object_hash[:6]
            object_dict['children'] = []

        if description is not None:
            object_dict['label'] += r'\n' + description

        return object_dict


def parse_tree(raw_content):
    children = []
    rest = raw_content
    while rest:
        mode, rest = rest.split(b' ', maxsplit=1)
        name, rest = rest.split(b'\x00', maxsplit=1)
        sha1, rest = rest[:20].hex(), rest[20:]
        children.append(parse_object(sha1, description=name.decode()))

    return children


def parse_commit(raw_content):
    content = raw_content.decode()
    content_lines = content.split('\n')
    commit_data = {}

    commit_data['tree'] = content_lines[0].split()[1]
    content_lines = content_lines[1:]

    commit_data['parents'] = []
    while content_lines[0].startswith('parent'):
        commit_data['parents'].append(content_lines[0].split()[1])
        content_lines = content_lines[1:]

    while content_lines[0].strip():
        key, *values = content_lines[0].split()
        commit_data[key] = ' '.join(values)
        content_lines = content_lines[1:]

    commit_data['message'] = '\n'.join(content_lines[1:]).strip()

    return [parse_object(commit_data['tree'])] + \
           [parse_object(parent) for parent in commit_data['parents']]


def get_last_commit():
    head_path = os.path.join(config['repo_path'], '.git', 'refs', 'heads', config['branch'])
    with open(head_path, 'r') as file:
        return file.read().strip()


def generate_dot(filename):
    trees = set()
    set_of_blobs = set()

    def recursive_write(file, tree):
        label = tree['label']
        for child in tree['children']:
            if child["label"].startswith("[blob]") and child["label"].endswith(config['file']):
                # file.write()
                set_of_blobs.add(f'"{label}" -> "{child["label"]}"\n')
                trees.add(label)
            recursive_write(file, child)

    def find_commit(file, tree):
        label = tree['label']

        for child in tree['children']:
            if child["label"] in trees:
                file.write(f'"{label}" -> "{child["label"]}"\n')
            find_commit(file, child)

    last_commit = get_last_commit()
    tree = parse_object(last_commit)
    with open(filename, 'w') as file:
        file.write('@startuml\n')
        recursive_write(file, tree)
        find_commit(file, tree)
        for blob in set_of_blobs:
            file.write(blob)
        file.write('@enduml')


def run_plantuml(plantuml_path, puml_file):
    subprocess.run(["java", "-jar", plantuml_path, puml_file])


if __name__ == "__main__":
    puml_file = "dependency_graph.puml"
    parser = argparse.ArgumentParser(description="Visualize git commit dependencies.")
    parser.add_argument("--graph-visualizer-path", required=True, help="Path to the PlantUML executable.")
    parser.add_argument("--repo-path", required=True, help="Path to the git repository.")
    parser.add_argument("--file", required=True, help="File name to filter commits by.")
    args = parser.parse_args()

    with open('config.json', 'r') as f:
        config = json.load(f)

    config['repo_path'] = args.repo_path
    config['file'] = args.file

    generate_dot(puml_file)
    run_plantuml(args.graph_visualizer_path, puml_file)
