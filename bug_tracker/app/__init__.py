
import os


from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from dotenv import load_dotenv

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bug_tracker.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'

    from app.routes.auth_routes import auth_bp
    from app.routes.bug_routes import bug_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(bug_bp)

    return app