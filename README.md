# Secure Syscall Interface

The **Secure Syscall Interface** is a web-based application designed to provide a secure and user-friendly interface for managing system calls. It includes features such as user authentication, file operations, syscall execution, and logging. The project is built using a Python backend with SQLite database and a responsive frontend.

---

## Features

### 1. User Authentication
- **Login**: Users can log in with their credentials to access the system.
- **Registration**: New users can register with a username, password, and role (e.g., `user` or `admin`).
- **Role-Based Access**: The application supports role-based access control for different functionalities.

### 2. File Operations
- **Read Files**: Users can read file content using the read syscall.
- **Write Files**: Users can write content to files using the write syscall.
- **File Management**: Users can open and close files using the open and close syscalls.
- **File Information**: Users can get file information using the stat syscall.

### 3. System Call Execution
- **Syscall Explorer**: Users can view available system calls including:
  - `open`: Open a file
  - `read`: Read from a file
  - `write`: Write to a file
  - `close`: Close a file
  - `getpid`: Get process ID
  - `stat`: Get file information
- **Execute Syscalls**: Users can select a syscall, provide parameters, and execute it securely.
- **Dynamic Parameters**: The interface dynamically adjusts based on the selected syscall's requirements.

### 4. Logging
- **Syscall Logs**: All executed syscalls are logged with details such as:
  - Username
  - Syscall name
  - Parameters
  - Result
  - Timestamp
- **Filter Logs**: Users can filter logs by username or syscall name.

### 5. Theme Toggle
- A theme toggle button allows users to switch between light and dark modes.

---

## Prerequisites

- Python 3.8 or higher
- SQLite (included with Python)
- `pip` for installing Python dependencies
- A modern web browser (e.g., Chrome, Firefox)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/secure-syscall-interface.git
   cd secure-syscall-interface
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**:
   ```bash
   python app.py
   ```

4. **Open the application**:
   Navigate to `http://localhost:5000` in your browser.

---

## Project Layout

The project is organized as follows:

```
Secure Syscall Interface/
│
├── app.py                    # Main Python backend application
├── requirements.txt          # Python dependencies
│
├── static/                   # Frontend static files
│   ├── index.html            # Main HTML file
│   ├── styles.css            # CSS for styling the application
│   ├── script.js             # JavaScript for frontend functionality
│
├── templates/                # Flask templates folder
│   └── index.html            # Main template file
│
└── data/                     # Folder for storing user-created files
```

---

## Usage

1. **Register**:
   - Navigate to the registration page.
   - Enter a username, password, and role.
   - Submit the form to create an account.

2. **Login**:
   - Enter your username and password on the login page.
   - Upon successful login, you'll be redirected to the syscall explorer dashboard.

3. **File Operations**:
   - Use the file input field to specify a file name.
   - Perform open, read, write, close, or stat operations as needed.

4. **Execute Syscalls**:
   - Select a syscall from the dropdown menu.
   - Provide the required parameters.
   - Execute the syscall and view the result.

5. **View Logs**:
   - Navigate to the logs section to view recent syscall logs.
   - Use filter options to narrow down logs by username or syscall name.

---

## API Endpoints

### Authentication
- **POST /api/register**
  - **Description**: Registers a new user.
  - **Request Body**: 
    ```json
    { "username": "string", "password": "string", "role": "string" }
    ```
  - **Response**: 
    ```json
    { "message": "User registered successfully" }
    ```
  - **Status**: 201 (Success), 400 (Invalid input)

- **POST /api/login**
  - **Description**: Authenticates a user.
  - **Request Body**: 
    ```json
    { "username": "string", "password": "string" }
    ```
  - **Response**: 
    ```json
    { "message": "Login successful", "token": "string" }
    ```
  - **Status**: 200 (Success), 401 (Unauthorized)

### Syscall Management
- **GET /api/syscalls**
  - **Description**: Fetches available syscalls.
  - **Response**: 
    ```json
    { "syscalls": ["open", "read", "write", "close", "getpid", "stat"] }
    ```
  - **Status**: 200 (Success)

- **POST /api/execute**
  - **Description**: Executes a specified syscall.
  - **Request Body**: 
    ```json
    { "syscall": "string", "params": { "param1": "value1", ... } }
    ```
  - **Response**: 
    ```json
    { "result": "string" }
    ```
  - **Status**: 200 (Success), 400 (Invalid syscall)

- **GET /api/logs**
  - **Description**: Retrieves syscall logs.
  - **Response**: 
    ```json
    { "logs": [{ "username": "string", "syscall": "string", "params": {}, "result": "string", "timestamp": "string" }] }
    ```
  - **Status**: 200 (Success)

---

## Security Considerations

- **Syscall Execution**: Syscalls are executed in a restricted environment to prevent unauthorized access.
- **Authentication**: Passwords are hashed using bcrypt before storage.
- **Input Validation**: All user inputs are sanitized to prevent common vulnerabilities.
- **Role-Based Access**: Admin users have elevated privileges, while regular users are restricted to safe operations.

---

## Troubleshooting

### Common Issues
- **Invalid Credentials**:
  - **Issue**: Login fails with an "Invalid credentials" error.
  - **Solution**: Ensure the username and password are correct.

- **File Descriptor Errors**:
  - **Issue**: File operations fail with descriptor errors.
  - **Solution**: Ensure files are opened correctly before performing operations.

- **Port Conflict**:
  - **Issue**: `http://localhost:5000` is not accessible.
  - **Solution**: Check if another service is using port 5000.

---

## Future Enhancements

- Add support for more syscall types.
- Implement advanced role-based access control.
- Improve logging with export options.
- Add unit tests for backend and frontend components.

---

## License

This project is licensed under the MIT License.

---

## Contributors

- Harsh Kumar, Aditya Gupta and Prakhar Mishra - Developer

---

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the backend framework.
- [SQLite](https://www.sqlite.org/) for database management.
- Open-source libraries for additional functionality.
