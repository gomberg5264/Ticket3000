import os
import logging
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        try:
            with open('users.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if parts[0] == user_id:
                        return User(parts[0], parts[1], ':'.join(parts[2:-1]), parts[-1] == 'True')
        except IOError as e:
            logger.error(f"Error reading users file: {e}")
        return None

    @staticmethod
    def get_all_users():
        users = []
        try:
            with open('users.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    users.append(User(parts[0], parts[1], ':'.join(parts[2:-1]), parts[-1] == 'True'))
        except IOError as e:
            logger.error(f"Error reading users file: {e}")
        return users

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.debug(f"Login attempt for username: {username}")
        try:
            with open('users.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if username == parts[1]:
                        stored_password = ':'.join(parts[2:-1])
                        if check_password_hash(stored_password, password):
                            user = User(parts[0], parts[1], stored_password, parts[-1] == 'True')
                            login_user(user, remember=True)  # Set remember=True
                            logger.info(f"User {username} logged in successfully")
                            return redirect(url_for('tickets.dashboard'))
            logger.warning(f"Invalid login attempt for username: {username}")
            flash('Invalid username or password')
        except IOError as e:
            logger.error(f"Error reading users file: {e}")
            flash('An error occurred. Please try again later.')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('tickets.dashboard'))
    users = User.get_all_users()
    return render_template('admin_dashboard.html', users=users)

@auth_bp.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('tickets.dashboard'))

    users = []
    try:
        with open('users.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if int(parts[0]) == user_id:
                    parts[-1] = 'False' if parts[-1] == 'True' else 'True'
                users.append(':'.join(parts) + '\n')

        with open('users.txt', 'w') as f:
            f.writelines(users)

        flash('User admin status updated successfully.')
    except IOError as e:
        logger.error(f"Error updating user admin status: {e}")
        flash('An error occurred while updating user admin status.')

    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('tickets.dashboard'))

    users = []
    try:
        with open('users.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if int(parts[0]) != user_id:
                    users.append(line)

        with open('users.txt', 'w') as f:
            f.writelines(users)

        flash('User deleted successfully.')
    except IOError as e:
        logger.error(f"Error deleting user: {e}")
        flash('An error occurred while deleting the user.')

    return redirect(url_for('auth.admin_dashboard'))

def create_admin_account():
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    print(f"Attempting to create admin account with username: {admin_username}")
    print(f"ADMIN_USERNAME environment variable: {admin_username}")
    print(f"ADMIN_PASSWORD environment variable: {'Set' if admin_password else 'Not set'}")

    if not admin_username or not admin_password:
        print("ADMIN_USERNAME or ADMIN_PASSWORD environment variable is not set. Skipping admin account creation.")
        return

    try:
        # Check if users.txt exists and if admin account already exists
        if os.path.exists('users.txt'):
            with open('users.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if parts[1] == admin_username:
                        print(f"Admin account with username '{admin_username}' already exists.")
                        return

        # If admin account doesn't exist, create it
        with open('users.txt', 'a') as f:
            hashed_password = generate_password_hash(admin_password)
            user_id = str(len(User.get_all_users()) + 1)  # Generate a unique user ID
            f.write(f"{user_id}:{admin_username}:{hashed_password}:True\n")
        print(f"Admin account created successfully with username: {admin_username}")
    except IOError as e:
        print(f"Error creating admin account: {e}")

# Initialize admin account when the module is imported
create_admin_account()

# Log the contents of users.txt after admin account creation
try:
    with open('users.txt', 'r') as f:
        users_content = f.read()
        print(f"Contents of users.txt:\n{users_content}")
except IOError as e:
    print(f"Error reading users.txt: {e}")

# Log all environment variables
print("All environment variables:")
for key, value in os.environ.items():
    if key in ['ADMIN_USERNAME', 'ADMIN_PASSWORD']:
        print(f"{key}: {'Set' if value else 'Not set'}")
    else:
        print(f"{key}: {value}")

print("Auth module initialized and admin account creation attempted.")
