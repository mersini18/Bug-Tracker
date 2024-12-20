import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import session
from app import create_app, db
from app.models import User
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
            password = bcrypt.hashpw('Password1'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.session.add(User(username='testuser', email='testuser@example.com', password=password, role='user'))
            db.session.add(User(username='admin', email='admin@example.com', password=password, role='admin'))
            db.session.commit()
        yield client

# Registration Tests
def test_register_valid(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Verify user exists in the database
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'

def test_register_duplicate_username(client):
    # Create a new user in the database
    response = client.post('/register', data={
        'username': 'newtestuser',
        'email': 'newtestuser@example.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Attempt to register with the same username
    response = client.post('/register', data={
        'username': 'newtestuser',  # Duplicate username
        'email': 'testusernew@example.com',  # Different email
        'password': 'Password123'
    }, follow_redirects=True)

    # Assert that the flash message is present in the response
    assert response.status_code == 200
    assert b"Username already exists!" in response.data


def test_login_valid(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'Password1'
    }, follow_redirects=False)

    # Check for redirect status code and target location
    assert response.status_code == 302  # HTTP redirect
    assert response.headers['Location'] == '/home/'  # Redirects to the dashboard
    # Check for flashed message
    with client.session_transaction() as session:
        flashed_messages = session['_flashes']
        assert ('success', 'Login successful!') in flashed_messages

def test_login_invalid(client):
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=False)
    
    # Check the response status code
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

    # Verify the flashed message in the session
    with client.session_transaction() as session:
        flashed_messages = session['_flashes']
        assert ('error', 'Invalid username or password') in flashed_messages

def test_logout(client):
    # Log in first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    # Then log out
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    #assert b"You have been logged out." in response.data
    assert session.get('user_id') is None