from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(80), unique=True, nullable=False)  # Unique username
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    email = db.Column(db.String(200), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' or 'admin'
    bugs_reported = db.relationship('Bug', foreign_keys='Bug.reported_by', backref='reporter', lazy=True)
    bugs_assigned = db.relationship('Bug', foreign_keys='Bug.assigned_to', backref='assignee', lazy=True)

# Project Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)  # Project name
    description = db.Column(db.Text, nullable=True)  # Optional project description
    bugs = db.relationship('Bug', backref='project', lazy=True)  # One-to-many relationship with bugs

# Bug Model
class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(200), nullable=False)  # Bug title
    description = db.Column(db.Text, nullable=False)  # Bug description
    status = db.Column(db.String(20), default='Open')  # Status: 'Open', 'In Progress', 'Resolved'
    priority = db.Column(db.String(10), default='Low')  # Priority: 'Low', 'Medium', 'High'
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # FK to User who reported the bug
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))  # FK to User assigned to fix the bug
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))  # FK to Project
