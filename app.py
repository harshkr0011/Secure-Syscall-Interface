# app.py
from flask import Flask, send_from_directory, request, jsonify
import config
from models import db, SysCallLog  # Add SysCallLog import
import auth
import syscall_handler

app = Flask(__name__, static_folder='static')
app.config.from_object('config')
db.init_app(app)

@app.route("/", methods=["GET"])
def serve_gui():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/register", methods=["POST"])
def register_endpoint():
    data = request.get_json()
    return auth.register(data.get("username"), data.get("password"), data.get("role", "user"))

@app.route("/login", methods=["POST"])
def login_endpoint():
    return auth.login()

@app.route("/syscall/<syscall_name>", methods=["POST"])
@auth.token_required
def syscall_endpoint(syscall_name):
    return syscall_handler.handle_syscall(syscall_name)

@app.route("/logs", methods=["GET"])
@auth.token_required
def get_logs():
    logs = SysCallLog.query.order_by(SysCallLog.timestamp.desc()).all()
    return jsonify([{
        "username": log.username,
        "syscall": log.syscall,
        "timestamp": log.timestamp.isoformat(),
        "status": log.status
    } for log in logs])

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)