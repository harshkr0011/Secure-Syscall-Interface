# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')

class SysCallLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    syscall = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), nullable=False)