// script.js
let token = null;
let userRole = null;

// Show registration form
document.getElementById('show-register').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('register-section').classList.remove('hidden');
});

// Show login form
document.getElementById('show-login').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('register-section').classList.add('hidden');
    document.getElementById('login-section').classList.remove('hidden');
});

// Handle registration
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;
    const responseEl = document.getElementById('register-response');

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();
        if (response.ok) {
            responseEl.textContent = `User registered successfully. You can now log in.`;
            responseEl.classList.add('success');
            responseEl.classList.remove('error');
        } else {
            responseEl.textContent = `Error: ${data.error}`;
            responseEl.classList.add('error');
            responseEl.classList.remove('success');
        }
    } catch (error) {
        responseEl.textContent = `Error: ${error.message}`;
        responseEl.classList.add('error');
        responseEl.classList.remove('success');
    }
});

// Handle login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const responseEl = document.getElementById('login-response');

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok) {
            token = data.token;
            userRole = data.role;
            responseEl.textContent = 'Login successful!';
            responseEl.classList.add('success');
            responseEl.classList.remove('error');
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('syscall-section').classList.remove('hidden');
            document.getElementById('user-role').textContent = `${username} (${userRole})`;
            controlSyscallButtons(userRole);
        } else {
            responseEl.textContent = `Error: ${data.error}`;
            responseEl.classList.add('error');
            responseEl.classList.remove('success');
        }
    } catch (error) {
        responseEl.textContent = `Error: ${error.message}`;
        responseEl.classList.add('error');
        responseEl.classList.remove('success');
    }
});

// Logout
document.getElementById('logout-button').addEventListener('click', () => {
    token = null;
    userRole = null;
    document.getElementById('syscall-section').classList.add('hidden');
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('login-form').reset();
    document.getElementById('login-response').textContent = '';
});

// Control visibility of syscall buttons based on role
function controlSyscallButtons(role) {
    document.getElementById('btn-read').style.display = 'inline-block';
    document.getElementById('btn-write').style.display = role === 'admin' ? 'inline-block' : 'none';
    document.getElementById('write-section').style.display = role === 'admin' ? 'block' : 'none';
    document.getElementById('btn-delete').style.display = role === 'admin' ? 'inline-block' : 'none';
}

// Write file syscall
async function writeFile() {
    const responseEl = document.getElementById('syscall-response');
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];

    if (!file) {
        responseEl.textContent = 'No file selected.';
        responseEl.classList.add('error');
        responseEl.classList.remove('success');
        return;
    }

    const reader = new FileReader();
    reader.onload = async () => {
        const fileContent = reader.result;

        try {
            const response = await fetch('/syscall/write_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ content: fileContent })
            });
            const data = await response.json();

            if (response.ok) {
                responseEl.textContent = `Success: ${JSON.stringify(data)}`;
                responseEl.classList.add('success');
                responseEl.classList.remove('error');
            } else {
                responseEl.textContent = `Error: ${data.error}`;
                responseEl.classList.add('error');
                responseEl.classList.remove('success');
            }
            refreshLogs();
        } catch (error) {
            responseEl.textContent = `Error: ${error.message}`;
            responseEl.classList.add('error');
            responseEl.classList.remove('success');
        }
    };
    reader.readAsText(file);
}

// Generic syscall handler
async function makeSyscall(syscallName) {
    const responseEl = document.getElementById('syscall-response');

    try {
        const response = await fetch(`/syscall/${syscallName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();

        if (response.ok) {
            responseEl.textContent = `Success: ${JSON.stringify(data)}`;
            responseEl.classList.add('success');
            responseEl.classList.remove('error');
        } else {
            responseEl.textContent = `Error: ${data.error}`;
            responseEl.classList.add('error');
            responseEl.classList.remove('success');
        }
        refreshLogs();
    } catch (error) {
        responseEl.textContent = `Error: ${error.message}`;
        responseEl.classList.add('error');
        responseEl.classList.remove('success');
    }
}

// Refresh and filter logs
async function refreshLogs() {
    const logsEl = document.getElementById('logs-output');
    const filterUser = document.getElementById('filter-user').value.toLowerCase();
    const filterSyscall = document.getElementById('filter-syscall').value.toLowerCase();

    try {
        const response = await fetch('/logs', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const logs = await response.json();
        console.log('Logs from server:', logs);  // Debug output
        if (Array.isArray(logs)) {
            const filteredLogs = logs.filter(log =>
                (!filterUser || log.username.toLowerCase().includes(filterUser)) &&
                (!filterSyscall || log.syscall.toLowerCase().includes(filterSyscall))
            );
            logsEl.textContent = filteredLogs.length > 0 
                ? filteredLogs.map(log => `${log.timestamp} ${log.username} - ${log.syscall} (${log.status})`).join('\n')
                : 'No matching logs found.';
        } else {
            logsEl.textContent = 'No logs available.';
        }
    } catch (error) {
        logsEl.textContent = `Error fetching logs: ${error.message}`;
    }
}