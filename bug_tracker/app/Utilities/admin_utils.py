import bcrypt
from flask import flash, redirect, url_for
from bug_tracker.app.models import User


def get_user_information_from_request(request, user_id):
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', '')
    password = request.form.get('password') or None

    return(User(id = user_id, username = username, email = email, role = role, password = password))

def validate_update_form_fields(form_information):
    # Validate form fields
        if not form_information.username or not form_information.email or not form_information.role:
            flash('All fields except password are required.', 'error')
            return redirect(url_for('admin.update_user_form', user_id=form_information.id))
        return None
        
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
      
def apply_user_update(user: User, data: User) -> None:
     user.username = data.username
     user.email = data.email
     user.role = data.role
     if data.password:
          user.password = hash_password(data.password)