from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, User

import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(User.username == username).first()
        if user and bcrypt.checkpw(password.encode('UTF-8'), user.password.encode('UTF-8')):
            flash('Login successful!', 'success')
            return redirect(url_for('bug_dashboard'))

        flash('Invalid username or password', 'error')
        return redirect(url_for('auth.login'))

        
    
    return render_template('login.html', show_navbar=False)

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        existingUser = User.query.filter((User.username == username) | (User.email == email)).first()
        if existingUser:
            flash('User already exists!', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())

        new_user = User(username=username, password=hashed_password.decode('UTF-8'), email=email, role = 'user')
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', show_navbar=False)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.register'))