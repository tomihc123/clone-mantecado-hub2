from app.modules.auth.repositories import UserRepository
from app.modules.auth.services import AuthenticationService
import pytest
from unittest.mock import patch, MagicMock
from app.modules.notepad.services import NotepadService
from app.modules.notepad.models import Notepad
from app.modules.auth.models import User
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from flask_login import current_user


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Crea un usuario confirmado en el contexto de prueba.
    """
    with test_client.application.app_context():
        # Crear y confirmar un usuario de prueba
        user = AuthenticationService().create_with_profile(
            name="Test",
            surname="User",
            email="user@example.com",
            password="test1234"
        )
        AuthenticationService().confirm_user_email(user.id)  # Confirmar email

        yield test_client

@pytest.fixture
def notepad_service():
    return NotepadService()

def test_get_all_by_user(notepad_service):
    with patch.object(notepad_service.repository, 'get_all_by_user') as mock_get_all:
        mock_notepads = [MagicMock(id=1), MagicMock(id=2)]
        mock_get_all.return_value = mock_notepads

        user_id = 1
        result = notepad_service.get_all_by_user(user_id)

        assert result == mock_notepads
        assert len(result) == 2
        mock_get_all.assert_called_once_with(user_id)

def test_create(notepad_service):
    with patch.object(notepad_service.repository, 'create') as mock_create:
        mock_notepad = MagicMock(id=1)
        mock_create.return_value = mock_notepad

        title = 'Test Notepad'
        body = 'Test Body'
        user_id = 1

        result = notepad_service.create(title=title, body=body, user_id=user_id)

        assert result == mock_notepad
        assert result.id == 1
        mock_create.assert_called_once_with(title=title, body=body, user_id=user_id)

def test_update(notepad_service):
    with patch.object(notepad_service.repository, 'update') as mock_update:
        mock_notepad = MagicMock(id=1)
        mock_update.return_value = mock_notepad

        notepad_id = 1
        title = 'Updated Notepad'
        body = 'Updated Body'

        result = notepad_service.update(notepad_id, title=title, body=body)

        assert result == mock_notepad
        mock_update.assert_called_once_with(notepad_id, title=title, body=body)

def test_delete(notepad_service):
    with patch.object(notepad_service.repository, 'delete') as mock_delete:
        mock_delete.return_value = True

        notepad_id = 1
        result = notepad_service.delete(notepad_id)

        assert result is True
        
@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


'''
def test_get_notepad(test_client):
    # Login del usuario confirmado
    login_response = test_client.post("/login", data=dict(email="user@example.com", password="test1234"), follow_redirects=True)
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Crear un notepad
    response = test_client.post('/notepad/create', data={
        'title': 'Notepad2',
        'body': 'This is the body of notepad2'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Confirmar la creación en la base de datos
    with test_client.application.app_context():
        user = UserRepository().get_by_email("user@example.com")
        notepad = Notepad.query.filter_by(title='Notepad2', user_id=user.id).first()
        assert notepad is not None, "The notepad was not found in the database."

    # Acceder a la página de detalles del notepad
    response = test_client.get(f'/notepad/{notepad.id}', follow_redirects=True)
    assert response.status_code == 200, "The notepad detail page could not be accessed."
    assert b'Notepad2' in response.data, "The notepad title is not present on the page after accessing details."

    test_client.get("/logout", follow_redirects=True)


def test_edit_notepad(test_client):
    # Login del usuario confirmado
    login_response = test_client.post("/login", data=dict(email="user@example.com", password="test1234"), follow_redirects=True)
    assert login_response.status_code == 200

    # Crear un notepad
    response = test_client.post('/notepad/create', data={
        'title': 'Notepad3',
        'body': 'This is the body of notepad3'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Confirmar la creación en la base de datos
    with test_client.application.app_context():
        user = UserRepository().get_by_email("user@example.com")
        notepad = Notepad.query.filter_by(title='Notepad3', user_id=user.id).first()
        assert notepad is not None, "The notepad was not found in the database."

    # Editar el notepad
    response = test_client.post(f'/notepad/edit/{notepad.id}', data={
        'title': 'Notepad3 Edited',
        'body': 'Edited body of notepad3.'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Verificar el cambio en el notepad editado en la base de datos
    with test_client.application.app_context():
        edited_notepad = Notepad.query.get(notepad.id)
        assert edited_notepad.title == 'Notepad3 Edited', "The notepad title was not updated in the database."
        assert edited_notepad.body == 'Edited body of notepad3.', "The notepad body was not updated in the database."

    test_client.get("/logout", follow_redirects=True)
    
 '''
 
    
def test_delete_notepad(test_client):
    login_response = test_client.post("/login", data=dict(email="user@example.com", password="test1234"), follow_redirects=True)
    assert login_response.status_code == 200

    # Crear un notepad para eliminar
    response = test_client.post('/notepad/create', data={
        'title': 'Notepad4',
        'body': 'Body of notepad4.'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Eliminar el notepad en el contexto de solicitud HTTP
    response = test_client.post('/notepad/delete/1', follow_redirects=True)
    assert response.status_code == 200

    # Verificar que el notepad fue eliminado
    response = test_client.get('/notepad')
    assert b'Notepad4' not in response.data, "The notepad title should not be present on the page after deletion."

    test_client.get("/logout", follow_redirects=True)