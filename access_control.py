from flask import request, jsonify
from models import User

permissions = {
    "admin": ["open", "read", "write", "close", "getpid", "stat"],
    "user": ["open", "read", "close", "getpid", "stat"]
}

def get_user_role(username):
    user = User.query.filter_by(username=username).first()
    return user.role if user else "guest"

def check_permission(syscall):
    username = request.user["username"]
    role = get_user_role(username)
    allowed_syscalls = permissions.get(role, [])
    if syscall not in allowed_syscalls:
        return False, jsonify({"error": f"Permission denied for {syscall}"})
    return True, None


