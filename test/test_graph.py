import pytest
from unittest.mock import patch, mock_open, call
import subprocess

# Импортируем функции для тестирования
from main import get_commit_dependencies, generate_puml, run_plantuml


# Тест для get_commit_dependencies
@patch("subprocess.run")
def test_get_commit_dependencies(mock_run):
    # Подготовка тестовых данных
    mock_run.return_value.stdout = "c1 p1\nc2 c1\nc3 c2 p2\n"
    repo_path = "/path/to/repo"
    file_hash = "testfilehash"

    # Ожидаемый результат
    expected_dependencies = {
        "c1": ["p1"],
        "c2": ["c1"],
        "c3": ["c2", "p2"]
    }

    # Вызов функции и проверка результата
    dependencies = get_commit_dependencies(repo_path, file_hash)
    assert dependencies == expected_dependencies

    # Проверка вызова subprocess.run с правильными параметрами
    mock_run.assert_called_once_with(
        ["git", "log", "--pretty=format:%H %P", "--", file_hash],
        cwd=repo_path,
        capture_output=True,
        text=True
    )


# Тест для generate_puml
@patch("builtins.open", new_callable=mock_open)
def test_generate_puml(mock_open):
    # Тестовые зависимости
    dependencies = {
        "c1": ["p1"],
        "c2": ["c1"],
        "c3": ["c2", "p2"]
    }

    # Ожидаемое содержимое файла .puml
    expected_output = """@startuml
"p1" --> "c1"
"c1" --> "c2"
"c2" --> "c3"
"p2" --> "c3"
@enduml
"""

    # Вызов функции
    generate_puml(dependencies, "output.puml")

    # Проверка правильности записи в файл
    mock_open.assert_called_once_with("output.puml", 'w')
    handle = mock_open()
    handle.write.assert_any_call("@startuml\n")
    handle.write.assert_any_call('"p1" --> "c1"\n')
    handle.write.assert_any_call('"c1" --> "c2"\n')
    handle.write.assert_any_call('"c2" --> "c3"\n')
    handle.write.assert_any_call('"p2" --> "c3"\n')
    handle.write.assert_any_call("@enduml\n")


# Тест для run_plantuml
@patch("subprocess.run")
def test_run_plantuml(mock_run):
    # Вызов функции
    plantuml_path = "/path/to/plantuml.jar"
    puml_file = "output.puml"
    run_plantuml(plantuml_path, puml_file)

    # Проверка вызова subprocess.run с правильными параметрами
    mock_run.assert_called_once_with(["java", "-jar", plantuml_path, puml_file])
