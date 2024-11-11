import hashlib
import pytest
from unittest.mock import MagicMock, patch
from app.modules.fakenodo.services import FakenodoService, checksum
from app.modules.fakenodo.models import Deposition
from app.modules.dataset.models import DataSet
from app.modules.featuremodel.models import FeatureModel
from app import create_app
from app import db
from sqlalchemy import inspect


@pytest.fixture
def fakenodo_service():
    return FakenodoService()


@pytest.fixture
def setup_deposition(app):
    with app.app_context():
        deposition = Deposition(id=1, dep_metadata={"title": "Test Deposition"}, status="draft", doi=None)
        db.session.add(deposition)
        db.session.commit()
        yield deposition
        db.session.delete(deposition)
        db.session.commit()
       
          
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", 
    })
    with app.app_context():
        inspector = inspect(db.engine)
        if "deposition" not in inspector.get_table_names():
            Deposition.__table__.create(db.engine)  
        yield app
        Deposition.__table__.drop(db.engine)


def test_create_new_deposition(fakenodo_service, app):
    with app.app_context():
        mock_dataset = MagicMock(spec=DataSet)
        mock_dataset.ds_meta_data.title = "Test Title"
        mock_dataset.ds_meta_data.publication_type.value = "none"
        mock_dataset.ds_meta_data.description = "Test Description"
        mock_dataset.ds_meta_data.authors = [MagicMock(name="Author1", affiliation="Test Affiliation",
                                                       orcid="0000-0000")]
        mock_dataset.ds_meta_data.tags = "test, dataset"

        with patch.object(fakenodo_service.deposition_repository, 'create_new_deposition', 
                          return_value=Deposition(id=1)) as mock_create:
            result = fakenodo_service.create_new_deposition(mock_dataset)
            assert result["id"] == 1
            assert result["metadata"]["title"] == "Test Title"
            assert result["message"] == "Deposition succesfully created in Fakenodo"
            mock_create.assert_called_once()


def test_upload_file(fakenodo_service, app):
    with app.app_context():
        mock_dataset = MagicMock(spec=DataSet)
        mock_feature_model = MagicMock(spec=FeatureModel)
        mock_feature_model.fm_meta_data.uvl_filename = "test_file.uvl"
        mock_user = MagicMock()
        mock_user.id = 1

        with patch("os.path.getsize", return_value=100), patch("app.modules.fakenodo.services.checksum", 
                                                               return_value="mocked_checksum"):
            result = fakenodo_service.upload_file(mock_dataset, 1, mock_feature_model, user=mock_user)
            assert result["id"] == 1
            assert result["file"] == "test_file.uvl"
            assert result["fileSize"] == 100
            assert result["checksum"] == "mocked_checksum"
            assert result["message"] == "File Uploaded to deposition with id 1"


def test_publish_deposition(fakenodo_service, app, setup_deposition):
    result = fakenodo_service.publish_deposition(setup_deposition.id)
    assert result["status"] == "published"
    assert result["conceptdoi"] == f"fakenodo.doi.{setup_deposition.id}"
    assert result["message"] == "Deposition published successfully in fakenodo."


def test_get_deposition(fakenodo_service, app, setup_deposition):
    result = fakenodo_service.get_deposition(setup_deposition.id)
    assert result["id"] == setup_deposition.id
    assert result["metadata"]["title"] == "Test Deposition"
    assert result["status"] == "draft"


def test_get_doi(fakenodo_service, app):
    with app.app_context():
        mock_deposition = MagicMock(spec=Deposition)
        mock_deposition.id = 1
        mock_deposition.doi = "fakenodo.doi.1"
        
        with patch.object(fakenodo_service, 'get_deposition', return_value={"doi": "fakenodo.doi.1"}):
            result = fakenodo_service.get_doi(1)
            assert result == "fakenodo.doi.1"


def test_checksum():
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b"test data"
        result = checksum("fake_file_path")
        assert result == hashlib.md5(b"test data").hexdigest()