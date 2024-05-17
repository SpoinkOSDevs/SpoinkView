from flask import Flask, redirect, url_for
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

# Route for root URL
@app.route('/')
def index():
    if not admin_account_exists():
        return redirect(url_for('setup_admin'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
