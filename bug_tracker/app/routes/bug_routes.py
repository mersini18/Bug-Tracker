from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User


bug_bp = Blueprint('bug', __name__, url_prefix='/home')

@bug_bp.route('/')
@login_required
def home():
    return render_template('home.html', username=current_user.username, show_navbar=True)