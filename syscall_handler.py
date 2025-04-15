# syscall_handler.py
from flask import request, jsonify
import access_control
from models import db, SysCallLog, User
import os
import ctypes
import json
import time

def handle_syscall(syscall_name, params=None):
    username = request.user["username"]
    print(f"Handling syscall: {syscall_name} for user: {username}")
    
    allowed, error = access_control.check_permission(syscall_name)
    if not allowed:
        print(f"Permission denied for {syscall_name}")
        log_action(username, syscall_name, params, "Permission denied")
        return error

    try:
        result = execute_syscall(syscall_name, params or {})
        log_action(username, syscall_name, params, result)
        return jsonify({"result": result})
    except Exception as e:
        error_msg = str(e)
        print(f"Error in syscall {syscall_name}: {error_msg}")
        log_action(username, syscall_name, params, f"Error: {error_msg}")
        return jsonify({"error": error_msg}), 500

def execute_syscall(syscall_name, params):
    # Load libc
    try:
        libc = ctypes.CDLL("libc.so.6")
    except:
        # For Windows testing, mock the system calls
        class MockLibc:
            def open(self, *args): return 3
            def read(self, *args): return 5
            def write(self, *args): return 5
            def close(self, *args): return 0
            def getpid(self): return 1234
            def stat(self, *args): return 0
        libc = MockLibc()

    if syscall_name == "open":
        if not params.get('filename'):
            raise ValueError("Filename required")
        fd = libc.open(to_cstring(params['filename']), 0)
        if fd == -1:
            raise RuntimeError("Failed to open file")
        return f"File descriptor: {fd}"

    elif syscall_name == "read":
        if not params.get('fd') or not params.get('size'):
            raise ValueError("File descriptor and size required")
        buf = ctypes.create_string_buffer(int(params['size']))
        bytes_read = libc.read(int(params['fd']), buf, int(params['size']))
        if bytes_read == -1:
            raise RuntimeError("Failed to read file")
        return f"Read {bytes_read} bytes: {buf.value.decode('utf-8', errors='ignore')}"

    elif syscall_name == "write":
        if not params.get('fd') or not params.get('content'):
            raise ValueError("File descriptor and content required")
        # Convert content to bytes if it's a string
        content = params['content']
        if isinstance(content, str):
            content = content.encode('utf-8')
        bytes_written = libc.write(int(params['fd']), to_cstring(content), len(content))
        if bytes_written == -1:
            raise RuntimeError("Failed to write to file")
        return f"Wrote {bytes_written} bytes"

    elif syscall_name == "close":
        if not params.get('fd'):
            raise ValueError("File descriptor required")
        result = libc.close(int(params['fd']))
        if result == -1:
            raise RuntimeError("Failed to close file")
        return "File closed successfully"

    elif syscall_name == "getpid":
        pid = libc.getpid()
        return f"Process ID: {pid}"

    elif syscall_name == "stat":
        if not params.get('filename'):
            raise ValueError("Filename required")
        class Stat(ctypes.Structure):
            _fields_ = [
                ("st_mode", ctypes.c_uint32),
                ("st_size", ctypes.c_int64),
                ("st_mtime", ctypes.c_int64),
            ]
        stat_buf = Stat()
        result = libc.stat(to_cstring(params['filename']), ctypes.byref(stat_buf))
        if result == -1:
            raise RuntimeError("Failed to stat file")
        return {
            "mode": stat_buf.st_mode,
            "size": stat_buf.st_size,
            "mtime": time.ctime(stat_buf.st_mtime)
        }

    else:
        raise ValueError(f"Unknown syscall: {syscall_name}")

def to_cstring(s):
    if isinstance(s, bytes):
        return ctypes.c_char_p(s)
    return ctypes.c_char_p(s.encode('utf-8'))

def log_action(username, syscall, params, result):
    try:
        log = SysCallLog(
            username=username,
            syscall=syscall,
            params=json.dumps(params) if params else "{}",
            result=str(result)
        )
        db.session.add(log)
        db.session.commit()
        print(f"Logged to DB: {username} - {syscall} - {result}")
    except Exception as e:
        db.session.rollback()
        print(f"DB logging error: {str(e)}")
