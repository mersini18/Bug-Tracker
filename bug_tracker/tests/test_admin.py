import pytest
import sys
import os
import bcrypt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models import User, Bug
from flask import url_for, get_flashed_messages

@pytest.fixture
def client():
    app = create_app({
    'TESTING' : True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', # In-memory DB
    'SECRET_KEY': 'test_secret_key'
    })
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])


    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Create admin and non-admin users
            password = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(username='admin', email='admin@test.com', password=password, role='admin')
            normal_user = User(username='user', email='user@test.com', password=password, role='user')
            db.session.add_all([admin_user, normal_user])
            db.session.commit()

        yield client

def test_admin_access_denied_for_non_admin(client):
    # Log in as a normal user
    response = client.post('/login', data={
        'username': 'user',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Attempt to access the admin dashboard
    response = client.get('/admin/dashboard', follow_redirects=False)  # Set follow_redirects=False to capture the redirection
    assert response.status_code == 302  # HTTP status code for redirection
    assert response.location == url_for('bug.home')  # Check if redirected to the homepage

def test_admin_access_granted(client):
    # Log in as an admin user
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Access the admin dashboard
    response = client.get('/admin/dashboard', follow_redirects=False)
    assert response.status_code == 200

def test_admin_delete_user(client):
    # Log in as an admin user
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Delete a user
    response = client.post('/admin/delete-user/2', follow_redirects=True)
    assert response.status_code == 200
    assert b"User deleted successfully" in response.data

    # Verify the user was deleted
    with client.application.app_context():
        user = User.query.filter_by(id=2).first()
        assert user is None



# TODO
# tests

def test_update_user_form(client):
    # Log in as an admin user
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Update an existing user
    response = client.post('/admin/update-user/2', data={
        'username': 'updated_user',
        'email': 'updated_email@example.com',
        'role': 'admin',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"User updated successfully!" in response.data

    # Verify the user data was updated
    with client.application.app_context():
        user = User.query.get(2)
        assert user is not None
        assert user.username == 'updated_user'
        assert user.email == 'updated_email@example.com'
        assert user.role == 'admin'
        # Optionally verify password hash if needed

@pytest.mark.skip
def test_update_user_form_invalid_data(client):
    # Log in as an admin user
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Attempt to update with missing data
    response = client.post('/admin/update-user/2', data={
        'username': '',
        'email': 'newemail@example.com',
        'role': 'user'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"All fields except password are required." in response.data

    # Verify the user data was not updated
    with client.application.app_context():
        user = User.query.get(2)
        assert user is not None
        assert user.username != ''  # Ensure original data is preserved

def test_add_user_success(client):
    # Log in as an admin user
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Add a new user
    response = client.post('/admin/add-user', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'role': 'user'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"New user added successfully!" in response.data

    # Verify the user was added
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.role == 'user'

def test_add_duplicate_user(client):
    # Log in as an admin user
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Add a user
    response = client.post('/admin/add-user', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password',
        'role': 'user'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Attempt to add the same user again
    response = client.post('/admin/add-user', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password',
        'role': 'user'
    }, follow_redirects=True)

    # Verify the flash message
    with client.session_transaction() as session:
        # Get all flashed messages using Flask's API
        flashed_messages = get_flashed_messages(with_categories=True)
        assert len(flashed_messages) > 0

        # Check for the specific error message
        category, message = flashed_messages[0]
        assert category == 'error'
        assert message == 'Username or email already exists.'
    # Ensure no duplicate user was added
    with client.application.app_context():
        user_count = User.query.filter_by(username='testuser').count()
        assert user_count == 1  # Ensure only one instance of the user exists

def test_add_user_missing_fields(client):
    # Log in as an admin user
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Attempt to add a user with missing fields
    response = client.post('/admin/add-user', data={
        'username': 'newuser',
        'email': '',
        'password': 'password123',
        'role': 'user'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"All fields are required!" in response.data

    # Ensure the user was not added
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is None
