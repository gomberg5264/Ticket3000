from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from auth import auth_bp, User
from tickets import tickets_bp
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ensure ADMIN_USERNAME is set
if 'ADMIN_USERNAME' not in os.environ:
    os.environ['ADMIN_USERNAME'] = 'admin'

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
