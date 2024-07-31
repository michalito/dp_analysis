import os
from flask import Flask, session
from flask_login import LoginManager
from .blueprints.main import main
from .blueprints.filtered import filtered
from .user_management import load_user
from .config import config

def create_app():
    app = Flask(__name__)
    
    env = os.environ.get('ENV', 'default')
    app.config.from_object(config[env])

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(user_id)

    # Register Blueprints
    app.register_blueprint(main)
    app.register_blueprint(filtered)

    # Initialize session variables before each request
    @app.before_request
    def initialize_globals():
        if 'uploaded_file_name' not in session:
            session['uploaded_file_name'] = None
        if 'current_file' not in session:
            session['current_file'] = 'input_sales_data.csv'
        if 'filtered_file' not in session:
            session['filtered_file'] = 'filtered_sales_data.csv'

    return app

# Create an app instance
app = create_app()
