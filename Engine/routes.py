from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from app import app, db
from models import User

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
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
        flash('You are not authorized to access this page.', 'error')
        return redirect(url_for('login'))

# Route for setup admin account
@app.route('/setup_admin', methods=['GET', 'POST'])
def setup_admin():
    if admin_account_exists():
        flash("Admin account already exists.", 'info')
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = 'Admin'
        password = 'Admin'
        new_admin = User(username=username, role='Admin')
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('setup_admin.html')

# Error handling for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Error handling for 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Check if an admin account exists in the database
def admin_account_exists():
    return User.query.filter_by(role='Admin').first() is not None
