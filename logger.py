import datetime

def log_action(username, syscall, status):
    log_entry = f"[{datetime.datetime.now().isoformat()}] {username} - {syscall} - {status}\n"
    with open("logs/syscall.log", "a") as f:
        f.write(log_entry)