import pytest
from unittest.mock import patch, mock_open, call
from main import get_commit_dependencies, generate_puml, run_plantuml


@patch("subprocess.run")
def test_get_commit_dependencies(mock_run):
    mock_run.return_value.stdout = "c1 p1\nc2 c1\nc3 c2 p2\n"
    repo_path = "/path/to/repo"
    file_hash = "testfilehash"

    expected_dependencies = {
        "c1": ["p1"],
        "c2": ["c1"],
        "c3": ["c2", "p2"]
    }
    expected_order = {
        "c1": 1,
        "c2": 2,
        "c3": 3
    }

    dependencies, commit_order = get_commit_dependencies(repo_path, file_hash)
    assert dependencies == expected_dependencies
    assert commit_order == expected_order

    mock_run.assert_called_once_with(
        ["git", "log", "--pretty=format:%H %P", "--", file_hash],
        cwd=repo_path,
        capture_output=True,
        text=True
    )


@patch("builtins.open", new_callable=mock_open)
def test_generate_puml(mocked_open):
    dependencies = {
        'c1': ['p1'],
        'c2': ['c1'],
        'c3': ['c2', 'p2'],
    }
    commit_order = {'p1': 4, 'c1': 1, 'c2': 2, 'c3': 3, 'p2': 5}

    expected_calls = [
        call('@startuml\n'),
        call('"4: p1" --> "1: c1"\n'),
        call('"1: c1" --> "2: c2"\n'),
        call('"2: c2" --> "3: c3"\n'),
        call('"5: p2" --> "3: c3"\n'),
        call('@enduml\n')
    ]

    generate_puml(dependencies, commit_order, "output.puml")
    mocked_open().write.assert_has_calls(expected_calls, any_order=False)


@patch("subprocess.run")
def test_run_plantuml(mock_run):
    plantuml_path = "/path/to/plantuml.jar"
    puml_file = "output.puml"

    run_plantuml(plantuml_path, puml_file)

    mock_run.assert_called_once_with(["java", "-jar", plantuml_path, puml_file])
