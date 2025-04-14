# app.py
from flask import Flask, send_from_directory, request, jsonify
import config
from models import db, User, SysCallLog
import auth
import syscall_handler
from flask_cors import CORS
import ctypes
import os
import stat
import time
import jwt
from datetime import datetime, timedelta
from functools import wraps
import json
import platform

# Platform-specific imports
if platform.system() == 'Linux':
    import pwd
    import grp
else:
    # Mock implementations for Windows
    class MockPwd:
        def getpwuid(self, uid):
            return type('obj', (object,), {'pw_name': 'user'})
    pwd = MockPwd()
    
    class MockGrp:
        def getgrgid(self, gid):
            return type('obj', (object,), {'gr_name': 'group'})
    grp = MockGrp()

app = Flask(__name__, static_folder='static')
CORS(app)
app.config.from_object('config')
db.init_app(app)

# Add favicon route
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return no content

@app.route("/", methods=["GET"])
def serve_gui():
    return send_from_directory(app.static_folder, 'index.html')

# API Routes
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "user")  # Default to "user" if role not provided
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
            
        return auth.register(username, password, role)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/login", methods=["POST"])
def login():
    try:
        return auth.login()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/api/syscalls", methods=["GET"])
@auth.token_required
def get_syscalls():
    syscalls = [
        {"name": "open", "description": "Opens a file, returns a file descriptor"},
        {"name": "read", "description": "Reads from a file descriptor"},
        {"name": "write", "description": "Writes to a file descriptor"},
        {"name": "close", "description": "Closes a file descriptor"},
        {"name": "getpid", "description": "Returns the process ID"},
        {"name": "stat", "description": "Gets file status"}
    ]
    return jsonify(syscalls)

@app.route("/api/execute", methods=["POST"])
@auth.token_required
def execute_syscall():
    data = request.get_json()
    syscall = data.get('syscall')
    params = data.get('params', {})
    user_role = request.user['role']

    print(f"Executing syscall: {syscall} with params: {params} for user: {request.user['username']}")

    # Initialize libc
    try:
        libc = ctypes.CDLL("libc.so.6")
        print("Successfully loaded libc")
    except Exception as e:
        print(f"Failed to load libc, using Windows implementation: {str(e)}")
        # For Windows, use Windows API
        class Stat(ctypes.Structure):
            _fields_ = [
                ("st_mode", ctypes.c_uint32),
                ("st_size", ctypes.c_int64),
                ("st_mtime", ctypes.c_int64),
            ]

        class MockLibc:
            def __init__(self):
                self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                self._setup_functions()
                self.open_files = {}  # Track open files
                self.next_fd = 3  # Start from 3 like Unix
                self.Stat = Stat  # Add reference to Stat structure
                
            def _setup_functions(self):
                # Setup CreateFile
                self.kernel32.CreateFileW.restype = ctypes.c_void_p
                self.kernel32.CreateFileW.argtypes = [
                    ctypes.c_wchar_p,  # lpFileName
                    ctypes.c_uint32,   # dwDesiredAccess
                    ctypes.c_uint32,   # dwShareMode
                    ctypes.c_void_p,   # lpSecurityAttributes
                    ctypes.c_uint32,   # dwCreationDisposition
                    ctypes.c_uint32,   # dwFlagsAndAttributes
                    ctypes.c_void_p    # hTemplateFile
                ]
                
                # Setup ReadFile
                self.kernel32.ReadFile.restype = ctypes.c_bool
                self.kernel32.ReadFile.argtypes = [
                    ctypes.c_void_p,   # hFile
                    ctypes.c_void_p,   # lpBuffer
                    ctypes.c_uint32,   # nNumberOfBytesToRead
                    ctypes.POINTER(ctypes.c_uint32),  # lpNumberOfBytesRead
                    ctypes.c_void_p    # lpOverlapped
                ]
                
                # Setup WriteFile
                self.kernel32.WriteFile.restype = ctypes.c_bool
                self.kernel32.WriteFile.argtypes = [
                    ctypes.c_void_p,   # hFile
                    ctypes.c_void_p,   # lpBuffer
                    ctypes.c_uint32,   # nNumberOfBytesToWrite
                    ctypes.POINTER(ctypes.c_uint32),  # lpNumberOfBytesWritten
                    ctypes.c_void_p    # lpOverlapped
                ]
                
                # Setup CloseHandle
                self.kernel32.CloseHandle.restype = ctypes.c_bool
                self.kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
                
                # Setup GetCurrentProcessId
                self.kernel32.GetCurrentProcessId.restype = ctypes.c_uint32
                self.kernel32.GetCurrentProcessId.argtypes = []
                
                # Setup GetFileAttributes
                self.kernel32.GetFileAttributesW.restype = ctypes.c_uint32
                self.kernel32.GetFileAttributesW.argtypes = [ctypes.c_wchar_p]
                
                # Setup GetFileSize
                self.kernel32.GetFileSize.restype = ctypes.c_uint32
                self.kernel32.GetFileSize.argtypes = [
                    ctypes.c_void_p,   # hFile
                    ctypes.POINTER(ctypes.c_uint32)  # lpFileSizeHigh
                ]
                
                # Setup GetFileTime
                self.kernel32.GetFileTime.restype = ctypes.c_bool
                self.kernel32.GetFileTime.argtypes = [
                    ctypes.c_void_p,   # hFile
                    ctypes.POINTER(ctypes.c_uint64),  # lpCreationTime
                    ctypes.POINTER(ctypes.c_uint64),  # lpLastAccessTime
                    ctypes.POINTER(ctypes.c_uint64)   # lpLastWriteTime
                ]
                
                # Constants
                self.GENERIC_READ = 0x80000000
                self.GENERIC_WRITE = 0x40000000
                self.FILE_SHARE_READ = 0x00000001
                self.FILE_SHARE_WRITE = 0x00000002
                self.OPEN_EXISTING = 3
                self.CREATE_ALWAYS = 2
                self.FILE_ATTRIBUTE_NORMAL = 0x00000080
                self.INVALID_HANDLE_VALUE = -1
                
            def open(self, filename, flags):
                if isinstance(filename, ctypes.c_char_p):
                    filename = filename.value.decode('utf-8')
                else:
                    filename = filename.decode('utf-8')
                    
                # Convert Windows path separators and get absolute path
                filename = os.path.abspath(filename.replace('/', '\\'))
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                # Check if file is already open
                for fd, (handle, path) in self.open_files.items():
                    if path == filename:
                        print(f"File {filename} is already open with fd {fd}")
                        return fd
                
                # Create the file if it doesn't exist
                if not os.path.exists(filename):
                    try:
                        with open(filename, 'w') as f:
                            pass
                    except Exception as e:
                        print(f"Failed to create file {filename}: {e}")
                        return -1
                
                handle = self.kernel32.CreateFileW(
                    filename,
                    self.GENERIC_READ | self.GENERIC_WRITE,
                    self.FILE_SHARE_READ | self.FILE_SHARE_WRITE,
                    None,
                    self.OPEN_EXISTING,  # Always use OPEN_EXISTING since we create the file above
                    self.FILE_ATTRIBUTE_NORMAL,
                    None
                )
                
                if handle == self.INVALID_HANDLE_VALUE:
                    error = ctypes.get_last_error()
                    print(f"Failed to open file: {filename}, error: {error}")
                    return -1
                    
                # Store the handle and return a new file descriptor
                fd = self.next_fd
                self.next_fd += 1
                self.open_files[fd] = (handle, filename)
                print(f"Opened file {filename} with fd {fd}")
                return fd
                
            def read(self, fd, buf, size):
                if fd not in self.open_files:
                    print(f"Invalid file descriptor: {fd}")
                    return -1
                    
                handle, filename = self.open_files[fd]
                bytes_read = ctypes.c_uint32(0)
                success = self.kernel32.ReadFile(
                    handle,
                    buf,
                    size,
                    ctypes.byref(bytes_read),
                    None
                )
                if not success:
                    error = ctypes.get_last_error()
                    print(f"Failed to read file {filename}, error: {error}")
                    return -1
                return bytes_read.value
                
            def write(self, fd, buf, size):
                if fd not in self.open_files:
                    print(f"Invalid file descriptor: {fd}")
                    return -1
                    
                handle, filename = self.open_files[fd]
                bytes_written = ctypes.c_uint32(0)
                success = self.kernel32.WriteFile(
                    handle,
                    buf,
                    size,
                    ctypes.byref(bytes_written),
                    None
                )
                if not success:
                    error = ctypes.get_last_error()
                    print(f"Failed to write file {filename}, error: {error}")
                    return -1
                return bytes_written.value
                
            def close(self, fd):
                if fd not in self.open_files:
                    print(f"Invalid file descriptor: {fd}")
                    return -1
                    
                handle, filename = self.open_files[fd]
                if not self.kernel32.CloseHandle(handle):
                    error = ctypes.get_last_error()
                    print(f"Failed to close file {filename}, error: {error}")
                    return -1
                    
                del self.open_files[fd]
                print(f"Closed file {filename} with fd {fd}")
                return 0
                
            def getpid(self):
                return self.kernel32.GetCurrentProcessId()
                
            def stat(self, filename, stat_buf):
                if isinstance(filename, ctypes.c_char_p):
                    filename = filename.value.decode('utf-8')
                else:
                    filename = filename.decode('utf-8')
                    
                # Convert Windows path separators and get absolute path
                filename = os.path.abspath(filename.replace('/', '\\'))
                
                # First try to get attributes
                attributes = self.kernel32.GetFileAttributesW(filename)
                if attributes == 0xFFFFFFFF:  # INVALID_FILE_ATTRIBUTES
                    error = ctypes.get_last_error()
                    print(f"Failed to get file attributes for {filename}, error: {error}")
                    return -1
                    
                # Try to open the file to get size and time
                handle = self.kernel32.CreateFileW(
                    filename,
                    self.GENERIC_READ,
                    self.FILE_SHARE_READ,
                    None,
                    self.OPEN_EXISTING,
                    self.FILE_ATTRIBUTE_NORMAL,
                    None
                )
                
                if handle == self.INVALID_HANDLE_VALUE:
                    error = ctypes.get_last_error()
                    print(f"Failed to open file for stat: {filename}, error: {error}")
                    return -1
                    
                try:
                    # Get file size
                    size_high = ctypes.c_uint32(0)
                    size_low = self.kernel32.GetFileSize(handle, ctypes.byref(size_high))
                    if size_low == 0xFFFFFFFF and ctypes.get_last_error() != 0:
                        print(f"Failed to get file size for {filename}")
                        return -1
                        
                    # Get file times
                    creation_time = ctypes.c_uint64(0)
                    last_access = ctypes.c_uint64(0)
                    last_write = ctypes.c_uint64(0)
                    if not self.kernel32.GetFileTime(handle, 
                                                   ctypes.byref(creation_time),
                                                   ctypes.byref(last_access),
                                                   ctypes.byref(last_write)):
                        print(f"Failed to get file times for {filename}")
                        return -1
                        
                    # Set stat information directly on the structure
                    stat_buf.contents.st_mode = 0o666  # Regular file with read/write permissions
                    stat_buf.contents.st_size = size_low
                    stat_buf.contents.st_mtime = last_write.value // 10000000 - 11644473600  # Convert to Unix time
                    return 0
                    
                finally:
                    self.kernel32.CloseHandle(handle)

        # Create a function to get or create the MockLibc instance
        def get_mock_libc():
            if not hasattr(app, 'mock_libc'):
                app.mock_libc = MockLibc()
                print("Created new MockLibc instance")
            else:
                print("Using existing MockLibc instance")
            return app.mock_libc

        # Use the function to get the MockLibc instance
        libc = get_mock_libc()

    try:
        if syscall == 'open':
            if not params.get('filename'):
                return jsonify({"error": "Filename required"}), 400
            print(f"Opening file: {params['filename']}")
            fd = libc.open(to_cstring(params['filename']), 0)
            if fd == -1:
                return jsonify({"error": "Failed to open file"}), 500
            result = f"File descriptor: {fd}"
            print(f"File opened successfully with fd: {fd}")
        elif syscall == 'read':
            if not params.get('fd') or not params.get('size'):
                return jsonify({"error": "File descriptor and size required"}), 400
            print(f"Reading from fd: {params['fd']} with size: {params['size']}")
            buf = ctypes.create_string_buffer(int(params['size']))
            bytes_read = libc.read(int(params['fd']), buf, int(params['size']))
            if bytes_read == -1:
                return jsonify({"error": "Failed to read file"}), 500
            result = f"Read {bytes_read} bytes: {buf.value.decode('utf-8', errors='ignore')}"
            print(f"Read successful: {result}")
        elif syscall == 'write':
            if not params.get('fd') or not params.get('content'):
                return jsonify({"error": "File descriptor and content required"}), 400
            print(f"Writing to fd: {params['fd']} with content: {params['content'][:100]}...")
            # Handle content encoding properly
            content = params['content']
            if isinstance(content, str):
                content = content.encode('utf-8')
            print(f"Content encoded to bytes, length: {len(content)}")
            bytes_written = libc.write(int(params['fd']), to_cstring(content), len(content))
            if bytes_written == -1:
                return jsonify({"error": "Failed to write to file"}), 500
            result = f"Wrote {bytes_written} bytes"
            print(f"Write successful: {result}")
        elif syscall == 'close':
            if not params.get('fd'):
                return jsonify({"error": "File descriptor required"}), 400
            print(f"Closing fd: {params['fd']}")
            result = libc.close(int(params['fd']))
            if result == -1:
                return jsonify({"error": "Failed to close file"}), 500
            result = "File closed successfully"
            print(f"Close successful: {result}")
        elif syscall == 'getpid':
            pid = libc.getpid()
            result = f"Process ID: {pid}"
            print(f"Getpid successful: {result}")
        elif syscall == 'stat':
            if not params.get('filename'):
                return jsonify({"error": "Filename required"}), 400
            print(f"Getting stat for file: {params['filename']}")
            stat_buf = libc.Stat()  # Use the Stat structure from libc
            stat_ptr = ctypes.pointer(stat_buf)
            result = libc.stat(to_cstring(params['filename']), stat_ptr)
            if result == -1:
                return jsonify({"error": "Failed to stat file"}), 500
            file_info = {
                "mode": stat_buf.st_mode,
                "size": stat_buf.st_size,
                "mtime": time.ctime(stat_buf.st_mtime)
            }
            result = json.dumps(file_info)
            print(f"Stat successful: {result}")
        else:
            return jsonify({"error": "Unsupported syscall"}), 400

        # Log the syscall execution
        log = SysCallLog(
            username=request.user['username'],
            syscall=syscall,
            params=json.dumps(params),
            result=str(result)
        )
        db.session.add(log)
        db.session.commit()
        print(f"Logged syscall execution to database")

        return jsonify({"result": result})
    except Exception as e:
        print(f"Error executing syscall: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs', methods=['GET'])
@auth.token_required
def get_logs():
    try:
        logs = SysCallLog.query.order_by(SysCallLog.timestamp.desc()).all()
        log_list = []
        for log in logs:
            try:
                params = json.loads(log.params) if log.params else {}
            except json.JSONDecodeError:
                params = {"error": "Invalid params format"}
            
            log_list.append({
                'username': log.username,
                'syscall': log.syscall,
                'params': params,
                'result': log.result,
                'timestamp': log.timestamp.isoformat() if log.timestamp else None
            })
        return jsonify(log_list)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch logs: {str(e)}"}), 500

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Helper functions
def to_cstring(s):
    if isinstance(s, ctypes.c_char_p):
        return s
    if isinstance(s, bytes):
        return s
    elif isinstance(s, str):
        return s.encode('utf-8')
    else:
        return str(s).encode('utf-8')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user = data
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)


    
