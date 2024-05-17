import subprocess
import psutil
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, current_user, logout_user

from app import app, db, login_manager
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username')
    return render_template('login.html')

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route for dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Admin':
        # Get system stats
        cpu_percent = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        return render_template('dashboard.html', cpu_percent=cpu_percent, mem_percent=mem_percent, disk_percent=disk_percent)
    else:
        flash('You are not authorized to access this page.')
        return redirect(url_for('login'))

# Route for calculator
@app.route('/calculator', methods=['POST'])
def calculator():
    try:
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        operation = request.form['operation']
        result = 0
        if operation == 'add':
            result = num1 + num2
        elif operation == 'subtract':
            result = num1 - num2
        elif operation == 'multiply':
            result = num1 * num2
        elif operation == 'divide':
            if num2 != 0:
                result = num1 / num2
            else:
                result = 'Error: Division by zero'
        return jsonify(result=result)
    except ValueError:
        return jsonify(result='Error: Invalid input')

# Route for setup admin account
@app.route('/setup_admin', methods=['GET', 'POST'])
def setup_admin():
    admin_user = User.query.filter_by(role='Admin').first()
    if admin_user:
        flash("Admin account already exists.")
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            new_admin = User(username=username, email=email, role='Admin')
            db.session.add(new_admin)
            db.session.commit()
            subprocess.run(['sudo', 'useradd', '-m', username])
            subprocess.run(['sudo', 'passwd', username], input=(password + '\n' + password + '\n').encode('utf-8'))
            flash('Admin account created successfully.')
            return redirect(url_for('login'))
        return render_template('setup_admin.html')
