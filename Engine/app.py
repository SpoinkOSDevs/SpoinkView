from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import User
from routes import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Check if an admin account exists in the database
def admin_account_exists():
    return User.query.filter_by(role='Admin').first() is not None

# Create admin account if it doesn't exist
def create_admin_account():
    if not admin_account_exists():
        admin = User(username='Admin', role='Admin')
        admin.set_password('Admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully.")
        print("Username: Admin")
        print("Password: Admin")

if __name__ == '__main__':
    create_admin_account()  # Create admin account on startup
    app.run(debug=True)
