# Secure Syscall Interface

A web-based application for securely handling system calls with role-based access control (RBAC), user authentication, and audit logging. Built using Flask (Python) for the backend, HTML/CSS/JavaScript for the frontend, and MySQL for persistent storage of users and logs.

## Table of Contents
- [Project Overview](#project-overview)
- [Project Layout](#project-layout)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Step-by-Step Usage](#step-by-step-usage)
- [MySQL Integration](#mysql-integration)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Project Overview
The Secure Syscall Interface allows users to perform system calls (e.g., read, write, delete files) based on their role (admin or user). It includes:
- User registration and login with JWT-based authentication.
- Role-based permissions (admins have more privileges than users).
- Logging of all system call activities stored in a MySQL database.
- A responsive frontend interface for interaction.

## Project Layout
```
secure-syscall-interface/
│
├── static/                  # Static files (Frontend)
│   ├── index.html          # Main HTML file
│   ├── script.js           # JavaScript logic
│   └── styles.css          # CSS styling
│
├── data/                   # Directory for sample data files
│   └── sample.txt          # Example file for read/write/delete operations
│
├── app.py                  # Flask application entry point
├── auth.py                 # Authentication logic (register, login, token)
├── config.py               # Configuration (DB URI, secret key)
├── models.py               # Database models (User, SysCallLog)
├── syscall_handler.py      # System call handling logic
├── access_control.py       # Role-based access control logic
│
└── README.md               # This file
```

**Note**: This project uses MySQL for all logging and user data storage via the `User` and `SysCallLog` tables. No flat log files (e.g., `syscall.log`) are used.

## Prerequisites
- **Python 3.8+**
- **MySQL 8.0+** (required for storing users and logs)
- Required Python packages:
  - `flask`
  - `flask-sqlalchemy`
  - `pyjwt`
  - `werkzeug`
  - `mysql-connector-python` (for MySQL)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd secure-syscall-interface
   ```

2. **Install Dependencies**
   Create a virtual environment and install required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install flask flask-sqlalchemy pyjwt werkzeug mysql-connector-python
   ```

3. **Set Up MySQL Database**
   - Install MySQL if not already installed (e.g., via `sudo apt install mysql-server` on Ubuntu or MySQL Installer on Windows).
   - Log in to MySQL:
     ```bash
     mysql -u root -p
     # Enter your MySQL root password
     ```
   - Create the database:
     ```sql
     CREATE DATABASE secure_syscall_db;
     EXIT;
     ```

4. **Configure Database Connection**
   - Open `config.py` and update the `SQLALCHEMY_DATABASE_URI` with your MySQL credentials:
     ```python
     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:<your_password>@localhost/secure_syscall_db'
     ```
   - Replace `<your_password>` with your MySQL root password or create a new user with appropriate privileges.

5. **Initialize the Database**
   - Run the Flask app to create the `user` and `syscall_log` tables:
     ```bash
     python app.py
     ```
   - The first run will initialize the database tables via `db.create_all()` in `app.py`. You may need to stop the app (Ctrl+C) and restart it afterward.

6. **Create Required Directories and Files**
   ```bash
   mkdir data
   touch data/sample.txt
   echo "Sample content" > data/sample.txt
   ```

7. **Run the Application**
   ```bash
   python app.py
   ```
   The app will run on `http://localhost:5000`.

## Step-by-Step Usage

1. **Access the Web Interface**
   Open a browser and navigate to `http://localhost:5000`.

2. **Register a User**
   - Click "Register here" on the login page.
   - Enter a username, password, and select a role (User or Admin).
   - Submit the form. If successful, you’ll see a confirmation message.

3. **Log In**
   - Return to the login page by clicking "Login here".
   - Enter your credentials and submit.
   - On successful login, you’ll see the system call interface.

4. **Perform System Calls**
   - **Read File**: Click "Read File" to display the contents of `data/sample.txt`.
   - **Write File** (Admin only): Upload a file and click "Write File" to overwrite `data/sample.txt`.
   - **Delete File** (Admin only): Click "Delete File" to remove `data/sample.txt`.
   - Responses will appear below the buttons.

5. **View Logs**
   - Scroll to the "Recent Logs" section.
   - Filter logs by username or syscall if desired.
   - Click "Refresh Logs" to update the log display from the MySQL database.

6. **Log Out**
   - Click "Logout" to return to the login page.

## MySQL Integration

### Database Schema
The project uses two tables managed by Flask-SQLAlchemy:

#### `user` Table
- **Columns**:
  - `id` (INT, PRIMARY KEY, AUTO_INCREMENT): Unique user ID.
  - `username` (VARCHAR(80), UNIQUE, NOT NULL): User’s username.
  - `password` (VARCHAR(255), NOT NULL): Hashed password.
  - `role` (VARCHAR(20), DEFAULT 'user'): User role (e.g., 'user' or 'admin').

#### `syscall_log` Table
- **Columns**:
  - `id` (INT, PRIMARY KEY, AUTO_INCREMENT): Unique log entry ID.
  - `username` (VARCHAR(80), NOT NULL): User who performed the syscall.
  - `syscall` (VARCHAR(120), NOT NULL): System call executed (e.g., 'read_file').
  - `timestamp` (DATETIME, DEFAULT CURRENT_TIMESTAMP): Time of the action.
  - `status` (VARCHAR(20), NOT NULL): Outcome (e.g., 'success' or 'failed').

### Manual Database Commands
These commands can be run in a MySQL client (e.g., `mysql -u root -p`) for setup, verification, or debugging:

1. **Create the Database** (if not already done):
   ```sql
   CREATE DATABASE secure_syscall_db;
   USE secure_syscall_db;
   ```

2. **Verify Tables** (after running `app.py`):
   ```sql
   SHOW TABLES;
   -- Expected output: 'user', 'syscall_log'
   ```

3. **View Users**:
   ```sql
   SELECT * FROM user;
   ```

4. **View Logs**:
   ```sql
   SELECT * FROM syscall_log ORDER BY timestamp DESC;
   ```

5. **Reset Database** (optional):
   ```sql
   DROP TABLE syscall_log;
   DROP TABLE user;
   ```
   - After dropping, rerun `python app.py` to recreate tables.

### Database Connection
- The connection is configured in `config.py`:
  ```python
  SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:<password>@localhost/secure_syscall_db'
  SECRET_KEY = '9a38d675fecc9eb835a0e882e6fc31cb'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  ```
- Ensure MySQL is running (`sudo service mysql start` on Linux or via services on Windows).

## Features
- **Authentication**: Secure login/register with JWT tokens.
- **Role-Based Access Control**: Admins can read, write, and delete; users can only read.
- **System Calls**: Basic file operations (read, write, delete).
- **Audit Logging**: Logs stored in the MySQL `syscall_log` table.
- **Responsive UI**: Clean, modern design with CSS styling.

## Troubleshooting
- **Database Connection Error**: Ensure MySQL is running and credentials in `config.py` match your setup (`mysql -u root -p` to test).
- **Permission Denied**: Verify user role in the `user` table and check `access_control.py` permissions.
- **File Not Found**: Confirm `data/sample.txt` exists and is readable/writable.
- **Logs Not Displaying**: Check the `syscall_log` table (`SELECT * FROM syscall_log;`) and ensure database operations succeed.
- **Tables Not Created**: Rerun `python app.py` and check for errors in the console.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---
