from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from auth import auth_bp, User, create_admin_account
from tickets import tickets_bp
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ensure ADMIN_USERNAME and ADMIN_PASSWORD are set
if 'ADMIN_USERNAME' not in os.environ:
    os.environ['ADMIN_USERNAME'] = 'admin'
if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin'  # Default password, should be changed in production

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(tickets_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('tickets.dashboard'))
    return redirect(url_for('auth.login'))

@app.context_processor
def inject_user():
    return dict(user=current_user)

def initialize_app():
    logger.info("Initializing application...")
    logger.info(f"ADMIN_USERNAME: {os.environ.get('ADMIN_USERNAME')}")
    logger.info(f"ADMIN_PASSWORD: {'Set' if os.environ.get('ADMIN_PASSWORD') else 'Not set'}")
    create_admin_account()
    logger.info("Admin account creation process completed.")

if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
