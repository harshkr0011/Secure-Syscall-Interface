# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')

class SysCallLog(db.Model):
    __tablename__ = 'syscall_log'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    syscall = db.Column(db.String(120), nullable=False)
    params = db.Column(db.Text, nullable=False)  # Store JSON string of parameters
    result = db.Column(db.Text, nullable=False)  # Store result string
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
