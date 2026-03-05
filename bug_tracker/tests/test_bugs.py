import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from flask import url_for
from app import create_app, db
from app.models import User, Bug, Project
import bcrypt

@pytest.fixture
def client():
    app = create_app({
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use an in-memory DB for tests
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

def test_add_bug_success(client):
    """
    Test if a user can successfully create a bug with valid data.
    """
    # Log in as the test user
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Submit valid data to the add_bug route
    response = client.post(url_for('bug.add_bug'), data={
        'title': 'Test Bug 2',
        'description': 'This is a test bug description.',
        'priority': 'High',
        'status': 'Not Started',
        'project_id': 1,  # Assuming test projects exist in the database
        'assigned_to': None  # Unassigned
    }, follow_redirects=True)

    # Assert the bug was created successfully
    assert response.status_code == 200

    # Verify the bug exists in the database
    with client.application.app_context():
        bug = Bug.query.filter_by(title='Test Bug 2').first()
        assert bug is not None
        assert bug.description == 'This is a test bug description.'
        assert bug.priority == 'High'
        assert bug.status == 'Not Started'
        assert bug.assigned_to is None

def test_add_bug_missing_fields(client):
    """
    Test if the system prevents bug creation when required fields are missing.
    """
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Submit invalid data with missing title
    response = client.post(url_for('bug.add_bug'), data={
        'description': 'This is a test bug description.',
        'priority': 'High',
        'status': 'Not Started',
        'project_id': 1,  # Assuming the test project has ID 1
        'assigned_to': None  # Unassigned
    }, follow_redirects=True)

    # Assert the bug was not created
    assert response.status_code == 200
    assert b"Title is required" in response.data or b"Error" in response.data

    # Verify the bug does not exist in the database
    with client.application.app_context():
        bug = Bug.query.filter_by(description='This is a test bug description.').first()
        assert bug is None

def test_delete_bug_as_admin(client):
    """Test that an admin can delete a bug."""
    with client.application.app_context():
        bug = Bug(
            title='Bug to Delete',
            description='Will be deleted.',
            priority='Low',
            status='Not Started',
            project_id=1,
            reported_by=2,
            assigned_to=None
        )
        db.session.add(bug)
        db.session.commit()
        bug_id = bug.id

    client.post('/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)

    response = client.post(f'/home/delete-bug/{bug_id}')
    assert response.status_code == 302

    with client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        messages = [msg for _, msg in flashes]
        assert "Bug deleted successfully." in messages

    with client.application.app_context():
        assert Bug.query.get(bug_id) is None

def test_delete_bug_as_non_admin(client):
    """Test that a non-admin cannot delete a bug."""
    with client.application.app_context():
        bug = Bug(
            title='Bug Not Deleted',
            description='Should remain.',
            priority='Low',
            status='Not Started',
            project_id=1,
            reported_by=1,
            assigned_to=None
        )
        db.session.add(bug)
        db.session.commit()
        bug_id = bug.id

    client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    response = client.post(f'/home/delete-bug/{bug_id}')
    assert response.status_code == 302

    with client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        messages = [msg for _, msg in flashes]
        assert "You do not have permission to delete bugs." in messages

    with client.application.app_context():
        assert Bug.query.get(bug_id) is not None

def test_delete_bug_not_found(client):
    """Test that deleting a non-existent bug returns 404."""
    client.post('/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)

    response = client.post('/home/delete-bug/9999')
    assert response.status_code == 404
