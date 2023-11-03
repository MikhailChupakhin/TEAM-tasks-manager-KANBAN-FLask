from flask import Flask
from dotenv import load_dotenv
import os

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from .filters import status_abbreviate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    load_dotenv()
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    db.init_app(app)
    migrate.init_app(app, db)
    csrf = CSRFProtect(app)

    from .models import User
    from .views import views
    from .auth import auth
    from .task_manager import task_manager_bp

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')
    app.register_blueprint(task_manager_bp, url_prefix='/task-manager')

    app.jinja_env.filters['status_abbreviate'] = status_abbreviate

    return app