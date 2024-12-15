import pytest
from unittest.mock import patch, MagicMock
from app.modules.community.services import CommunityService
from app.modules.auth.models import User
from app import db
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(owner_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


@pytest.fixture
def community_service():
    return CommunityService()


def test_get_all(community_service):
    with patch.object(community_service.repository, 'get_all') as mock_get_all:
        mock_community = [MagicMock(id=1), MagicMock(id=2)]
        mock_get_all.return_value = mock_community

        result = community_service.get_all()

        assert result == mock_community
        assert len(result) == 2
        mock_get_all.assert_called_once()


def test_create(community_service):
    with patch.object(community_service.repository, 'create') as mock_create:
        mock_community = MagicMock(id=1)
        mock_create.return_value = mock_community

        name = 'Test Community'
        description = 'Test description'
        owner_id = 1

        result = community_service.create(name=name, description=description, owner_id=owner_id)

        assert result == mock_community
        assert result.id == 1
        mock_create.assert_called_once_with(name=name, description=description, owner_id=owner_id)


def test_update(community_service):
    with patch.object(community_service.repository, 'update') as mock_update:
        mock_community = MagicMock(id=1)
        mock_update.return_value = mock_community

        community_id = 1
        name = 'Updated community'
        description = 'Updated description'

        result = community_service.update(community_id, name=name, description=description)

        assert result == mock_community
        mock_update.assert_called_once_with(community_id, name=name, description=description)


def test_delete(community_service):
    with patch.object(community_service.repository, 'delete') as mock_delete:
        mock_delete.return_value = True

        community_id = 1
        result = community_service.delete(community_id)

        assert result is True
