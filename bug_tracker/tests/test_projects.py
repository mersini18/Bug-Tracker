import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import User, Project
import bcrypt


@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_secret_key',
        'WTF_CSRF_ENABLED': False
    })
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            # Create test users
            password = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.session.add(User(username='testuser', email='testuser@example.com', password=password, role='user'))
            db.session.add(User(username='admin', email='admin@example.com', password=password, role='admin'))
            db.session.add(Project(name="Test Project 2", description="Test Project Description 2"))
            db.session.commit()
        yield client


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_list_projects(client):
    """Test that a logged-in user can view the projects list and sees seeded data."""
    client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    response = client.get('/projects/projects')
    assert response.status_code == 200
    assert b'Test Project 2' in response.data


def test_add_project_success(client):
    """Test that a logged-in user can create a project with a valid name and description."""
    client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    response = client.post('/projects/add-project', data={
        'name': 'New Test Project',
        'description': 'A valid project description.'
    }, follow_redirects=True)

    assert response.status_code == 200

    with client.application.app_context():
        project = Project.query.filter_by(name='New Test Project').first()
        assert project is not None
        assert project.description == 'A valid project description.'


# ---------------------------------------------------------------------------
# Validation / sad paths
# ---------------------------------------------------------------------------

def test_add_project_missing_name(client):
    """Test that project creation fails and nothing is persisted when the name field is empty."""
    client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    response = client.post('/projects/add-project', data={
        'name': '',
        'description': 'Description with no name.'
    }, follow_redirects=True)

    assert response.status_code == 200

    with client.application.app_context():
        project = Project.query.filter_by(description='Description with no name.').first()
        assert project is None


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------

def test_delete_project_as_admin(client):
    """Test that an admin can delete a project and receives the success flash message."""
    with client.application.app_context():
        project = Project(name='Project To Delete', description='Will be removed.')
        db.session.add(project)
        db.session.commit()
        project_id = project.id

    client.post('/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)

    response = client.post(f'/projects/delete-project/{project_id}')
    assert response.status_code == 302

    with client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        messages = [msg for _, msg in flashes]
        assert 'Project deleted successfully.' in messages

    with client.application.app_context():
        assert Project.query.get(project_id) is None


def test_delete_project_as_non_admin(client):
    """Test that a non-admin is blocked from deleting a project and receives the permission-denied flash message."""
    with client.application.app_context():
        project = Project(name='Project Not Deleted', description='Should remain.')
        db.session.add(project)
        db.session.commit()
        project_id = project.id

    client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    response = client.post(f'/projects/delete-project/{project_id}')
    assert response.status_code == 302

    with client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        messages = [msg for _, msg in flashes]
        assert 'You do not have permission to delete projects.' in messages

    with client.application.app_context():
        assert Project.query.get(project_id) is not None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_delete_project_not_found(client):
    """Test that deleting a non-existent project returns 404."""
    client.post('/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)

    response = client.post('/projects/delete-project/9999')
    assert response.status_code == 404
