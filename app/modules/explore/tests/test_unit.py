import pytest
from app import create_app  # Assuming you have a function to create your app instance
from app.modules.explore.repositories import ExploreRepository
from unittest.mock import MagicMock

@pytest.fixture
def app():
    app = create_app()  # Create the Flask app instance (you might already have this)
    app.app_context().push()  # Push the app context so db.session is available
    return app

@pytest.fixture
def explore_repository():
    return ExploreRepository()

@pytest.fixture
def mock_query():
    # Mock the db session query to avoid hitting the actual database
    return MagicMock()

def test_filter_datasets_by_author(explore_repository, mock_query, app):
    # Your test code
    query_string = "author:John Doe"
    explore_repository.filter_datasets(query_string)

def test_filter_datasets_by_tags(explore_repository, mock_query, app):
    # Your test code
    query_string = "tags:python"
    explore_repository.filter_datasets(query_string)

def test_filter_datasets_by_min_size(explore_repository, mock_query, app):
    # Your test code
    query_string = "min_size:1000"
    explore_repository.filter_datasets(query_string)

def test_filter_datasets_by_publication_type(explore_repository, mock_query, app):
    # Your test code
    query_string = "publication_type:journal"
    explore_repository.filter_datasets(query_string)


from unittest.mock import MagicMock

@pytest.fixture
def mock_query():
    # Mock the db session query to avoid hitting the actual database
    mock_query = MagicMock()
    mock_query.all.return_value = []  # You can customize this to return test data
    return mock_query

