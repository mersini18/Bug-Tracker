import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
