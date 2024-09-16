from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from auth import auth_bp, User, create_admin_account
from tickets import tickets_bp
import os
import logging
import sys
from datetime import timedelta

# Set up logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Session configuration
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Ensure ADMIN_USERNAME and ADMIN_PASSWORD are set
if 'ADMIN_USERNAME' not in os.environ:
    os.environ['ADMIN_USERNAME'] = 'admin'
    print("ADMIN_USERNAME not found in environment variables. Setting default value: 'admin'")
if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin'  # Default password, should be changed in production
    print("ADMIN_PASSWORD not found in environment variables. Setting default value: 'admin'")

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
    print("Initializing application...")
    print(f"ADMIN_USERNAME: {os.environ.get('ADMIN_USERNAME')}")
    print(f"ADMIN_PASSWORD: {'Set' if os.environ.get('ADMIN_PASSWORD') else 'Not set'}")
    
    # Log all environment variables
    print("All environment variables:")
    for key, value in os.environ.items():
        if key in ['ADMIN_USERNAME', 'ADMIN_PASSWORD']:
            print(f"{key}: {'Set' if value else 'Not set'}")
        else:
            print(f"{key}: {value}")
    
    create_admin_account()
    print("Admin account creation process completed.")

    # Print contents of users.txt
    try:
        with open('users.txt', 'r') as f:
            print("Contents of users.txt:")
            print(f.read())
    except IOError as e:
        print(f"Error reading users.txt: {e}")

if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
