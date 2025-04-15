# Secure Syscall Interface

The **Secure Syscall Interface** is a web-based application designed to provide a secure and user-friendly interface for managing system calls. It includes features such as user authentication, file operations, syscall execution, and logging. The project is built using a Python backend with a MySQL database and a responsive frontend.

---

## Features

### 1. User Authentication
- **Login**: Users can log in with their credentials to access the system.
- **Registration**: New users can register with a username, password, and role (e.g., `user` or `admin`).
- **Role-Based Access**: The application supports role-based access control for different functionalities.

### 2. File Operations
- **Read Files**: Users can specify a file name and read its content.
- **Write Files**: Users can create new files and write content to them.
- **Update Files**: Users can update the content of existing files.
- **Delete Files**: Users can delete files they no longer need.

### 3. System Call Execution
- **Syscall Explorer**: Users can view available system calls.
- **Execute Syscalls**: Users can select a syscall, provide parameters, and execute it securely.
- **Dynamic Parameters**: The interface dynamically adjusts based on the selected syscall's requirements.

### 4. Logging
- **Syscall Logs**: All executed syscalls are logged with details such as username, syscall name, parameters, result, and timestamp.
- **Filter Logs**: Users can filter logs by username or syscall name for easier analysis.

### 5. Theme Toggle
- A theme toggle button allows users to switch between light and dark modes for better usability.

---

## Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- `pip` for installing Python dependencies
- MySQL command-line tool for database setup
- A modern web browser (e.g., Chrome, Firefox)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/harshkr0011/Secure-Syscall-Interface
   cd secure-syscall-interface
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   Run the `setup_database.sql` script in your MySQL server:
   ```bash
   mysql -u root -p < setup_database.sql
   ```

4. **Start the backend server**:
   ```bash
   python app.py
   ```

5. **Open the application**:
   Navigate to `http://localhost:5000` in your browser.

---

## Project Layout

The project is organized as follows:

```
Secure Syscall Interface/
│
├── app.py                    # Main Python backend application
├── setup_database.sql        # SQL script to set up the database schema
├── requirements.txt          # Python dependencies
│
├── static/                   # Frontend static files
│   ├── index.html            # Main HTML file
│   ├── styles.css            # CSS for styling the application
│   ├── script.js             # JavaScript for frontend functionality
│
├── templates/                # Optional Flask templates folder
│
├── data/                     # Folder for storing user-created files
│   └── sample.txt            # Example file
│
└── logs/                     # Folder for storing application logs
    └── app.log               # Log file for debugging and error tracking
```

---

## Usage

1. **Register**:
   - Navigate to the registration page.
   - Enter a username, password, and role.
   - Submit the form to create an account.

2. **Login**:
   - Enter your username and password on the login page.
   - Upon successful login, you’ll be redirected to the syscall explorer dashboard.

3. **File Operations**:
   - Use the file input field to specify a file name.
   - Perform read, write, update, or delete operations as needed.

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
- **POST /register**
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

- **POST /login**
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

### File Operations
- **GET /read-file?filename=string**
  - **Description**: Reads the content of a specified file.
  - **Response**: 
    ```json
    { "filename": "string", "content": "string" }
    ```
  - **Status**: 200 (Success), 404 (File not found)

- **POST /write-file**
  - **Description**: Writes content to a new file.
  - **Request Body**: 
    ```json
    { "filename": "string", "content": "string" }
    ```
  - **Response**: 
    ```json
    { "message": "File written successfully" }
    ```
  - **Status**: 201 (Success), 400 (Invalid input)

- **PUT /update-file**
  - **Description**: Updates the content of an existing file.
  - **Request Body**: 
    ```json
    { "filename": "string", "content": "string" }
    ```
  - **Response**: 
    ```json
    { "message": "File updated successfully" }
    ```
  - **Status**: 200 (Success), 404 (File not found)

### Syscall Management
- **GET /api/syscalls**
  - **Description**: Fetches available syscalls.
  - **Response**: 
    ```json
    { "syscalls": ["syscall1", "syscall2", ...] }
    ```
  - **Status**: 200 (Success)

- **POST /api/execute**
  - **Description**: Executes a specified syscall.
  - **Request Body**: 
    ```json
    { "syscall": "string", "parameters": ["string", ...] }
    ```
  - **Response**: 
    ```json
    { "result": "string", "status": "success" }
    ```
  - **Status**: 200 (Success), 400 (Invalid syscall)

---

## Security Considerations

- **Syscall Execution**: Syscalls are executed in a restricted environment to prevent unauthorized access or system-level damage.
- **Authentication**: Passwords are hashed using bcrypt before storage in the database.
- **Input Validation**: All user inputs are sanitized to prevent SQL injection, XSS, and other common vulnerabilities.
- **Role-Based Access**: Admin users have elevated privileges, while regular users are restricted to safe operations.

---

## Troubleshooting

### Common Issues
- **Invalid Credentials**:
  - **Issue**: Login fails with an "Invalid credentials" error.
  - **Solution**: Ensure the username and password are correct. Verify that the password is hashed correctly in the database.

- **Database Connection Errors**:
  - **Issue**: Application fails to connect to MySQL.
  - **Solution**: Verify the database credentials in `app.py`. Ensure the MySQL server is running and accessible.

- **File Descriptor Errors**:
  - **Issue**: File operations fail with descriptor errors.
  - **Solution**: Ensure files are opened correctly before performing operations. Check file permissions in the `data/` folder.

- **Port Conflict**:
  - **Issue**: `http://localhost:5000` is not accessible.
  - **Solution**: Check if another service is using port 5000. Change the port in `app.py` if needed (e.g., `app.run(port=5001)`).

- **Dependency Issues**:
  - **Issue**: Errors during `pip install -r requirements.txt`.
  - **Solution**: Ensure compatibility with libraries like `libc` (especially on Windows). Use a virtual environment to isolate dependencies.

---

## Future Enhancements

- Add support for more syscall types and parameter configurations.
- Implement advanced role-based access control with granular permissions.
- Improve logging with export options (e.g., CSV, JSON).
- Add unit tests for backend and frontend components.
- Integrate a CI/CD pipeline for automated testing and deployment.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributors

- Rakul - Developer

---

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the backend framework.
- [MySQL](https://www.mysql.com/) for database management.
- Open-source libraries for additional functionality.

---

This README provides a clear, professional, and comprehensive overview of the project. It includes all requested sections, improved formatting, and additional details to ensure developers and users can easily set up and understand the application. If you need further tweaks or additional sections, let me know!
