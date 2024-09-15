import os
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        with open('users.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if parts[0] == user_id:
                    return User(parts[0], parts[1], ':'.join(parts[2:-1]), parts[-1] == 'True')
        return None

    @staticmethod
    def get_all_users():
        users = []
        with open('users.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                users.append(User(parts[0], parts[1], ':'.join(parts[2:-1]), parts[-1] == 'True'))
        return users

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open('users.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if username == parts[1]:
                    stored_password = ':'.join(parts[2:-1])
                    if check_password_hash(stored_password, password):
                        user = User(parts[0], parts[1], stored_password, parts[-1] == 'True')
                        login_user(user)
                        return redirect(url_for('tickets.dashboard'))
        flash('Invalid username or password')
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
    with open('users.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if int(parts[0]) == user_id:
                parts[-1] = 'False' if parts[-1] == 'True' else 'True'
            users.append(':'.join(parts) + '\n')

    with open('users.txt', 'w') as f:
        f.writelines(users)

    flash('User admin status updated successfully.')
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('tickets.dashboard'))

    users = []
    with open('users.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if int(parts[0]) != user_id:
                users.append(line)

    with open('users.txt', 'w') as f:
        f.writelines(users)

    flash('User deleted successfully.')
    return redirect(url_for('auth.admin_dashboard'))

# Initialize users.txt if it doesn't exist
if not os.path.exists('users.txt'):
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    with open('users.txt', 'w') as f:
        f.write(f"1:{admin_username}:{generate_password_hash('admin')}:True\n")
