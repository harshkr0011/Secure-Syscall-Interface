# syscall_handler.py
from flask import request, jsonify
import access_control
from models import db, SysCallLog
import os

def handle_syscall(syscall_name):
    username = request.user["username"]
    print(f"Handling syscall: {syscall_name} for user: {username}")  # Debug
    allowed, error = access_control.check_permission(syscall_name)
    if not allowed:
        print(f"Permission denied for {syscall_name}")  # Debug
        log_action(username, syscall_name, "failed")
        return error

    try:
        if syscall_name == "read_file":
            print("Attempting to read file")  # Debug
            with open("data/sample.txt", "r") as f:
                content = f.read()
            log_action(username, syscall_name, "success")
            return jsonify({"data": content})
        elif syscall_name == "write_file":
            print("Attempting to write file")  # Debug
            content = request.get_json().get("content")
            with open("data/sample.txt", "w") as f:
                f.write(content)
            log_action(username, syscall_name, "success")
            return jsonify({"message": "File written"})
        elif syscall_name == "delete_file":
            print("Attempting to delete file")  # Debug
            os.remove("data/sample.txt")
            log_action(username, syscall_name, "success")
            return jsonify({"message": "File deleted"})
        else:
            print(f"Unknown syscall: {syscall_name}")  # Debug
            log_action(username, syscall_name, "failed")
            return jsonify({"error": "Unknown syscall"}), 400
    except Exception as e:
        print(f"Error in syscall {syscall_name}: {str(e)}")  # Debug
        log_action(username, syscall_name, "failed")
        return jsonify({"error": str(e)}), 500

def log_action(username, syscall, status):
    try:
        log = SysCallLog(username=username, syscall=syscall, status=status)
        db.session.add(log)
        db.session.commit()
        print(f"Logged to DB: {username} - {syscall} - {status}")  # Debug
    except Exception as e:
        db.session.rollback()
        print(f"DB logging error: {str(e)}")  # Debug