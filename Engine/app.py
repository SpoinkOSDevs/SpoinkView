from flask import Flask
from models import db, User

app = Flask(__name__)

# Load configuration from the models file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications to improve performance

# Initialize the SQLAlchemy object with the Flask app
db.init_app(app)

# Import routes after initializing app and db to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
