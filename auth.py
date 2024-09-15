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
                id, username, password, is_admin = line.strip().split(':')
                if id == user_id:
                    return User(id, username, password, is_admin == 'True')
        return None

    @staticmethod
    def get_all_users():
        users = []
        with open('users.txt', 'r') as f:
            for line in f:
                id, username, password, is_admin = line.strip().split(':')
                users.append(User(id, username, password, is_admin == 'True'))
        return users

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open('users.txt', 'r') as f:
            for line in f:
                id, stored_username, stored_password, is_admin = line.strip().split(':')
                if username == stored_username and check_password_hash(stored_password, password):
                    user = User(id, stored_username, stored_password, is_admin == 'True')
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
            id, username, password, is_admin = line.strip().split(':')
            if int(id) == user_id:
                is_admin = 'False' if is_admin == 'True' else 'True'
            users.append(f"{id}:{username}:{password}:{is_admin}\n")

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
            id, username, password, is_admin = line.strip().split(':')
            if int(id) != user_id:
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
