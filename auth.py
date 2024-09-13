import os
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        with open('users.txt', 'r') as f:
            for line in f:
                id, username, password = line.strip().split(':')
                if id == user_id:
                    return User(id, username, password)
        return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open('users.txt', 'r') as f:
            for line in f:
                id, stored_username, stored_password = line.strip().split(':')
                if username == stored_username and check_password_hash(stored_password, password):
                    user = User(id, stored_username, stored_password)
                    login_user(user)
                    return redirect(url_for('tickets.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')

        with open('users.txt', 'r') as f:
            users = f.readlines()

        for user in users:
            if username == user.split(':')[1]:
                flash('Username already exists')
                return render_template('register.html')

        new_user_id = str(len(users) + 1)
        hashed_password = generate_password_hash(password)
        new_user = f"{new_user_id}:{username}:{hashed_password}\n"

        with open('users.txt', 'a') as f:
            f.write(new_user)

        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Initialize users.txt if it doesn't exist
if not os.path.exists('users.txt'):
    with open('users.txt', 'w') as f:
        f.write(f"1:admin:{generate_password_hash('admin')}\n")
