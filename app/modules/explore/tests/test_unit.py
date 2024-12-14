from app.modules.explore.services import ExploreService
import pytest
from app import create_app  # Assuming you have a function to create your app instance
from app.modules.explore.repositories import ExploreRepository
from unittest.mock import MagicMock


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():  # Contexto gestionado
        yield app


@pytest.fixture
def explore_repository():
    return ExploreRepository()


@pytest.fixture
def mock_query():
    # Mock the db session query to avoid hitting the actual database
    mock_query = MagicMock()
    mock_query.all.return_value = []
    return mock_query


@pytest.fixture
def mock_repository(mocker):
    # Crear un mock para el repositorio utilizado por el servicio
    mock_repo = mocker.patch('app.modules.explore.services.ExploreService')
    return mock_repo


def test_filter_datasets_by_author(explore_repository, mock_query, app):

    query_string = "author:John Doe"
    explore_repository.filter_datasets(query_string)


def test_filter_datasets_by_tags(explore_repository, mock_query, app):

    query_string = "tags:tag1"
    explore_repository.filter_datasets(query_string)


def test_filter_datasets_by_tags2(explore_repository, mock_query, app):

    query_string = "tags:tag1,tag2"
    explore_repository.filter_datasets(query_string)


def test_filter_datasets_by_min_size(explore_repository, mock_query, app):

    query_string = "min_size:1000"
    explore_repository.filter_datasets(query_string)


def test_filter_datasets_by_max_size(explore_repository, mock_query, app):

    query_string = "max_size:1000"
    explore_repository.filter_datasets(query_string)


def test_filter_invalid_query():
    mock_repository = MagicMock()

    mock_repository.filter_datasets.return_value = []

    service = ExploreService()
    service.repository = mock_repository

    query_string = "invalid:query"

    try:
        results = service.filter(query_string)

        mock_repository.filter_datasets.assert_called_once_with(
            query_string, "newest", [], "any"
        )

        assert results == []

        call_args = mock_repository.filter_datasets.call_args
        assert call_args[0][0] == "invalid:query"
    except Exception as e:
        assert False, f"Unexpected exception occurred: {e}"


def test_filter_empty_query():
    mock_repository = MagicMock()

    mock_repository.filter_datasets.return_value = []

    service = ExploreService()
    service.repository = mock_repository

    query_string = ""

    try:
        results = service.filter(query_string)

        mock_repository.filter_datasets.assert_called_once_with(
            query_string, "newest", [], "any"
        )

        assert results == []

    except Exception as e:
        assert False, f"Unexpected exception occurred: {e}"
