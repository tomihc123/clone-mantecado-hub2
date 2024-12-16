import pytest
from app import db
from app.modules.fakenodo.models import Deposition
from app.modules.fakenodo.repositories import DepositionRepository


@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


def test_sample_assertion(test_client):
    """
    Sample test to verify that the test framework and environment are working correctly.
    It does not communicate with the Flask application; it only performs a simple assertion to
    confirm that the tests in this module can be executed.
    """
    greeting = "Hello, World!"
    assert greeting == "Hello, World!", "The greeting does not coincide with 'Hello, World!'"


@pytest.fixture(scope="module")
def setup_test_data():
    """
    Configures the test database with initial data for testing.
    """
    try:
        db.session.rollback()  # Rollback por si hay transacciones pendientes
        db.session.query(Deposition).delete()  # Clear existing data

        depo1 = Deposition(meta_data={"title": "Test Dataset 1", "description": "First test dataset"}, status="draft")
        depo2 = Deposition(meta_data={"title": "Test Dataset 2", "description": "Second test dataset"},
                           status="published")
        depo3 = Deposition(meta_data={"title": "Test Dataset 3", "description": "Third test dataset"}, status="draft")

        db.session.add_all([depo1, depo2, depo3])
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    yield

    db.session.rollback()
    db.session.query(Deposition).delete()
    db.session.commit()


def test_create_deposition(setup_test_data):
    """
    Test creating a new deposition.
    """
    repo = DepositionRepository()
    metadata = {"title": "New Test Dataset", "description": "Description"}
    new_depo = repo.createDeposition(metadata=metadata, doi="fakenodo.test.doi")

    assert new_depo.id is not None, "Deposition ID should be generated."
    assert new_depo.doi == "fakenodo.test.doi", "DOI does not match the expected value."
    assert new_depo.meta_data["title"] == "New Test Dataset", f"Metadata mismatch: {new_depo.meta_data}"
    assert new_depo.meta_data["description"] == "Description", f"Metadata mismatch: {new_depo.meta_data}"


def test_retrieve_deposition(setup_test_data):
    """
    Test retrieving an existing deposition by ID.
    """
    depo = Deposition.query.first()  # Retrieve an existing deposition

    assert depo is not None, "Deposition should exist in the database."
    assert depo.meta_data["title"] == "Test Dataset 1", "Deposition metadata title mismatch."


def test_update_deposition(setup_test_data):
    """
    Test updating an existing deposition.
    """
    depo = Deposition.query.first()
    depo.meta_data["title"] = "Updated Test Dataset"
    db.session.commit()

    updated_depo = Deposition.query.get(depo.id)
    assert updated_depo.meta_data[
        "title"] == "Updated Test Dataset", f"Deposition update failed. Got {updated_depo.meta_data['title']}"


def test_delete_deposition(setup_test_data):
    """
    Test deleting an existing deposition.
    """
    depo = Deposition.query.first()
    depo_id = depo.id

    db.session.delete(depo)
    db.session.commit()

    deleted_depo = Deposition.query.get(depo_id)
    assert deleted_depo is None, "Deposition was not deleted successfully."
