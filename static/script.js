// script.js
let token = null;
let userRole = null;

// Load theme on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    loadSyscalls();
});

// Toggle theme
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Show/hide sections
document.getElementById('show-register').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('register-section').classList.remove('hidden');
});

document.getElementById('show-login').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('register-section').classList.add('hidden');
    document.getElementById('login-section').classList.remove('hidden');
});

// Register
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;
    const responseEl = document.getElementById('register-response');

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();

        if (response.ok) {
            responseEl.textContent = 'Registration successful! Please login.';
            responseEl.classList.add('success');
            document.getElementById('register-section').classList.add('hidden');
            document.getElementById('login-section').classList.remove('hidden');
        } else {
            responseEl.textContent = data.error || 'Registration failed';
            responseEl.classList.add('error');
        }
    } catch (error) {
        responseEl.textContent = `Error: ${error.message}`;
        responseEl.classList.add('error');
    }
});

// Login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const responseEl = document.getElementById('login-response');

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();

        if (response.ok) {
            token = data.token;
            userRole = data.role;
            localStorage.setItem('token', token);
            localStorage.setItem('userRole', userRole);
            responseEl.textContent = 'Login successful!';
            responseEl.classList.add('success');
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('syscall-section').classList.remove('hidden');
            document.getElementById('user-role').textContent = `${username} (${userRole})`;
            loadSyscalls();
            refreshLogs();
        } else {
            responseEl.textContent = data.error || 'Login failed';
            responseEl.classList.add('error');
        }
    } catch (error) {
        responseEl.textContent = `Error: ${error.message}`;
        responseEl.classList.add('error');
    }
});

// Logout
document.getElementById('logout-button').addEventListener('click', () => {
    token = null;
    userRole = null;
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    document.getElementById('syscall-section').classList.add('hidden');
    document.getElementById('login-section').classList.remove('hidden');
});

// Load system calls
async function loadSyscalls() {
    try {
        const response = await fetch('/api/syscalls', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const syscalls = await response.json();
        const syscallItems = document.getElementById('syscall-items');
        const syscallSelect = document.getElementById('syscall-select');

        // Populate list
        syscallItems.innerHTML = syscalls.map(sc => `
            <div class="syscall-item">
                <h4>${sc.name}</h4>
                <p>${sc.description}</p>
            </div>
        `).join('');

        // Populate dropdown
        syscallSelect.innerHTML = '<option value="">Select a syscall</option>' +
            syscalls.map(sc => `<option value="${sc.name}">${sc.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading syscalls:', error);
    }
}

// Dynamic form fields based on syscall
document.getElementById('syscall-select').addEventListener('change', (e) => {
    const syscall = e.target.value;
    const paramsDiv = document.getElementById('syscall-params');
    paramsDiv.innerHTML = '';

    if (syscall === 'open' || syscall === 'stat') {
        paramsDiv.innerHTML = `
            <label>Filename:</label>
            <input type="text" id="param-filename" placeholder="e.g., /tmp/test.txt" required>
        `;
    } else if (syscall === 'read') {
        paramsDiv.innerHTML = `
            <label>File Descriptor:</label>
            <input type="number" id="param-fd" placeholder="e.g., 3" required>
            <label>Size:</label>
            <input type="number" id="param-size" placeholder="e.g., 1024" required>
        `;
    } else if (syscall === 'write') {
        paramsDiv.innerHTML = `
            <label>File Descriptor:</label>
            <input type="number" id="param-fd" placeholder="e.g., 3" required>
            <label>Content:</label>
            <textarea id="param-content" placeholder="Content to write" required></textarea>
        `;
    } else if (syscall === 'close') {
        paramsDiv.innerHTML = `
            <label>File Descriptor:</label>
            <input type="number" id="param-fd" placeholder="e.g., 3" required>
        `;
    }
});

// Execute syscall
document.getElementById('syscall-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const syscall = document.getElementById('syscall-select').value;
    const responseEl = document.getElementById('syscall-response');
    let params = {};

    if (syscall === 'open' || syscall === 'stat') {
        params.filename = document.getElementById('param-filename').value;
    } else if (syscall === 'read') {
        params.fd = document.getElementById('param-fd').value;
        params.size = document.getElementById('param-size').value;
    } else if (syscall === 'write') {
        params.fd = document.getElementById('param-fd').value;
        params.content = document.getElementById('param-content').value;
    } else if (syscall === 'close') {
        params.fd = document.getElementById('param-fd').value;
    }

    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ syscall, params })
        });
        const data = await response.json();

        if (response.ok) {
            responseEl.textContent = `Success: ${JSON.stringify(data.result)}`;
            responseEl.classList.add('success');
            responseEl.classList.remove('error');
            refreshLogs();
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

// Refresh logs
async function refreshLogs() {
    try {
        const response = await fetch('/api/logs', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch logs');
        }
        
        const logs = await response.json();
        const logsContainer = document.getElementById('logs-output');
        logsContainer.innerHTML = '';
        
        logs.forEach(log => {
            const logElement = document.createElement('div');
            logElement.className = 'log-entry';
            logElement.innerHTML = `
                <div class="log-header">
                    <span class="log-username">${log.username}</span>
                    <span class="log-syscall">${log.syscall}</span>
                    <span class="log-timestamp">${new Date(log.timestamp).toLocaleString()}</span>
                </div>
                <div class="log-content">
                    <p><strong>Parameters:</strong> ${JSON.stringify(log.params)}</p>
                    <p><strong>Result:</strong> ${log.result}</p>
                </div>
            `;
            logsContainer.appendChild(logElement);
        });
    } catch (error) {
        console.error('Error fetching logs:', error);
        const logsContainer = document.getElementById('logs-output');
        logsContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

// Theme toggle functionality
document.addEventListener("DOMContentLoaded", () => {
    const toggleThemeButton = document.getElementById("toggle-theme");

    // Check for saved theme preference in localStorage
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
    }

    toggleThemeButton.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        // Save the user's preference in localStorage
        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });
});
