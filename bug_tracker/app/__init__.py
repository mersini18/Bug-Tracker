
import os


from flask import Flask
from app.models import db
# from app.routes.bug_routes import bug_bp
# from app.routes.admin_routes import admin_bp

from dotenv import load_dotenv



def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bug_tracker.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)

    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    # app.register_blueprint(bug_bp)
    # app.register_blueprint(admin_bp)

    return app