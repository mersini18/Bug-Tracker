from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User
from functools import wraps

import bcrypt

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("You do not have permission to use this page", "error")
            return redirect(url_for('bug.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def dashboard():
    users= User.query.all()
    return render_template('admin_dashboard.html', users=users)

@admin_bp.route('/update-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_user_form(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')

        # Validate form fields
        if not username or not email or not role:
            flash('All fields except password are required.', 'error')
            return redirect(url_for('admin.update_user_form', user_id=user_id))
        
        user.username = username
        user.email = email
        user.role = role

        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.password = hashed_password

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    # Render update user form
    return render_template('update_user.html', user=user)

@admin_bp.route('/add-user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Input validation
        if not username or not email or not password:
            flash("All fields are required!", "error")
            return render_template('add_user.html')
        
        # Check for existing user
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.", "error")
            return render_template('add_user.html')

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create new user
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("New user added successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('add_user.html')

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully!", 'success')
    return redirect(url_for('admin.dashboard'))
    