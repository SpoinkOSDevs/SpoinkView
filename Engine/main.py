# main.py

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

# Define the BackupUser class
class BackupUser(Base):
    __tablename__ = 'backup_users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Add an admin user to both tables
admin_user = User(username='Admin', password='Admin')
session.add(admin_user)

backup_admin_user = BackupUser(username='Admin', password='Admin')
session.add(backup_admin_user)

session.commit()
session.close()

# After creating tables and adding users, call app.py
import app
