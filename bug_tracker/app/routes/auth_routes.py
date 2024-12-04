from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/register')
def register():
    return render_template('register.html')

@auth_bp.route('/')
def home():
    return '<h1>Welcome to the Bug Tracker'