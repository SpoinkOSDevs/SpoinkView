# main.py

import os
import subprocess
import sys
import argparse
from flask import Flask, g
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)

# Define the path to the database in a system-wide accessible directory
DATABASE_PATH = '/var/lib/flask_app/users.db'
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

# Ensure the directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Define the SQLAlchemy engine
try:
    engine = create_engine(DATABASE_URI, echo=True)
except Exception as e:
    logging.error("Failed to create SQLAlchemy engine: %s", e)
    exit(1)

# Create a base class
Base = declarative_base()

# Define the User class
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

# Create tables in the database
try:
    Base.metadata.create_all(engine)
except Exception as e:
    logging.error("Failed to create database tables: %s", e)
    exit(1)

# Define a function to get the database session
def get_session():
    if 'session' not in g:
        Session = sessionmaker(bind=engine)
        g.session = Session()
    return g.session

# Close the database session at the end of the request
@app.teardown_appcontext
def close_session(exception=None):
    session = g.pop('session', None)
    if session is not None:
        session.close()

# Add an admin user if not already present
@app.before_request
def create_admin_user():
    session = get_session()
    admin_user = session.query(User).filter_by(username='Admin').first()
    if not admin_user:
        try:
            admin_user = User(username='Admin', password='Admin')
            session.add(admin_user)
            session.commit()
        except Exception as e:
            logging.error("Failed to add admin user to the database: %s", e)
            exit(1)

# Define a route
@app.route('/')
def hello():
    return 'Hello, Flask is running on port 8000!'

def create_systemd_service():
    service_file_path = '/etc/systemd/system/flask_app.service'
    service_content = f"""\
[Unit]
Description=Flask App Service
After=network.target

[Service]
User={os.getlogin()}
Group=${os.getgroups()[0]}
WorkingDirectory={os.getcwd()}
ExecStart=/usr/bin/python {os.path.abspath(__file__)}
Restart=always

[Install]
WantedBy=multi-user.target
"""

    with open(service_file_path, 'w') as f:
        f.write(service_content)

    try:
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
        subprocess.run(['sudo', 'systemctl', 'enable', 'flask_app.service'])
        logging.debug("Created and enabled systemd service.")
    except Exception as e:
        logging.error("Failed to create and enable systemd service: %s", e)

def run_flask_app():
    # Run Flask app on port 8000
    try:
        app.run(debug=True, port=8000, threaded=True)
    except Exception as e:
        logging.error("Failed to run Flask app: %s", e)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Flask app.')
    parser.add_argument('-P', '--persistent', action='store_true', help='Run Flask app as a persistent service.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    if args.persistent:
        create_systemd_service()
    else:
        run_flask_app()
