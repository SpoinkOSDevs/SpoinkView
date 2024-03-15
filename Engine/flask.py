
import subprocess
import psutil
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

# Initialize database
try:
    db.create_all()
except OperationalError:
    pass

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
        return "You are not authorized to access this page."

# Route for calculator
@app.route('/calculator', methods=['POST'])
def calculator():
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

# Route for setup admin account
@app.route('/setup_admin', methods=['GET', 'POST'])
def setup_admin():
    admin_user = User.query.filter_by(role='Admin').first()
    if admin_user:
        return "Admin account already exists."
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

if __name__ == '__main__':
    app.run(debug=True)
