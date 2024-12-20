from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.forms import RegisterForm
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
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('bug.home'))

        flash('Invalid username or password', 'error')
        return redirect(url_for('auth.login'))

        
    
    return render_template('login.html', show_navbar=False)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():  # Form validation success
        # Check for existing user
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists!", "error")
            return redirect(url_for('auth.register'))

        # Create new user
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))
    else:  # Form validation failed
        # Handle specific validation errors and flash them
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field.capitalize()}: {error}", "error")

    return render_template('register.html', form=form, show_navbar=False)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.register'))