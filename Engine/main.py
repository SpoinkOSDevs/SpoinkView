# main.py

from flask import Flask
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create Flask app
app = Flask(__name__)

# Define the SQLAlchemy engine
engine = create_engine('sqlite:///users.db', echo=True)

# Create a base class
Base = declarative_base()

# Define the User class
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Add an admin user if not already present
admin_user = session.query(User).filter_by(username='Admin').first()
if not admin_user:
    admin_user = User(username='Admin', password='Admin')
    session.add(admin_user)
    session.commit()

# Define a route
@app.route('/')
def hello():
    return 'Hello, Flask is running in the background!'

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
