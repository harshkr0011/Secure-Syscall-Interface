# audit_tool.py
import json
import os

LOG_FILE = "logs/syscall.log"

def read_logs(filter_user=None, filter_syscall=None):
    if not os.path.exists(LOG_FILE):
        return []

    logs = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            if filter_user and entry["username"] != filter_user:
                continue
            if filter_syscall and entry["syscall"] != filter_syscall:
                continue
            logs.append(entry)
    return logs

if __name__ == "__main__":
    print(read_logs(filter_user="admin"))