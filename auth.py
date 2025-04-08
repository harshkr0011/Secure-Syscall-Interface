# auth.py
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from models import db, User
from config import SECRET_KEY

def register(username, password, role):
    if not username or not password or not role:
        return jsonify({"error": "All fields are required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = jwt.encode({
            "username": user.username,
            "role": user.role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY)
        return jsonify({"token": token, "role": user.role})
    return jsonify({"error": "Invalid credentials"}), 401

def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Token is missing"}), 401
        try:
            token = token.split(" ")[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator