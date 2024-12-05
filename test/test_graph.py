import pytest
from unittest.mock import patch, mock_open
from main import parse_commit, parse_object, generate_dot, get_last_commit, run_plantuml

@pytest.fixture
def mock_config():
    with patch.dict('main.config', {
        'repo_path': '/mock/repo',
        'branch': 'main',
        'file': 'test_file'
    }):
        yield


def test_get_last_commit(mock_config):
    # Тестируем получение последнего коммита
    head_content = "123456abcdef\n"
    with patch('builtins.open', mock_open(read_data=head_content)):
        result = get_last_commit()
        assert result == "123456abcdef"


def test_parse_object_invalid_hash(mock_config):
    # Тестируем случай, когда объект с таким хешем не существует
    object_hash = 'nonexistent_hash'
    with patch('builtins.open', side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            parse_object(object_hash)


def test_run_plantuml(mock_config):
    # Тестируем вызов subprocess для запуска PlantUML
    with patch('subprocess.run') as mock_run:
        run_plantuml('/mock/path/to/plantuml.jar', 'dependency_graph.puml')
        mock_run.assert_called_with(["java", "-jar", '/mock/path/to/plantuml.jar', 'dependency_graph.puml'])

