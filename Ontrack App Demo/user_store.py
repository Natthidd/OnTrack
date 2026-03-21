import json
import os
from datetime import datetime

# ── paths ──────────────────────────────────────────────────────────────────────
_DIR       = os.path.dirname(os.path.abspath(__file__))
_DB_FILE   = os.path.join(_DIR, "users.json")
_SES_FILE  = os.path.join(_DIR, "session.json")
_TASK_FILE = os.path.join(_DIR, "tasks.json")

# ── in-memory cache ────────────────────────────────────────────────────────────
_users: dict = {}   # email -> {"username": str, "password": str}
_tasks: dict = {}   # email -> [ {task dict}, ... ]


# ── internal helpers ───────────────────────────────────────────────────────────
def _load_users():
    global _users
    if os.path.exists(_DB_FILE):
        try:
            with open(_DB_FILE, "r", encoding="utf-8") as f:
                _users = json.load(f)
        except Exception:
            _users = {}

def _save_users():
    with open(_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(_users, f, ensure_ascii=False, indent=2)

def _load_tasks():
    global _tasks
    if os.path.exists(_TASK_FILE):
        try:
            with open(_TASK_FILE, "r", encoding="utf-8") as f:
                _tasks = json.load(f)
        except Exception:
            _tasks = {}

def _save_tasks():
    with open(_TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(_tasks, f, ensure_ascii=False, indent=2)

def _serialize_task(task: dict) -> dict:
    t = dict(task)
    if isinstance(t.get("due_dt"), datetime):
        t["due_dt"] = t["due_dt"].isoformat()
    return t

def _deserialize_task(t: dict) -> dict:
    t = dict(t)
    if isinstance(t.get("due_dt"), str):
        t["due_dt"] = datetime.fromisoformat(t["due_dt"])
    return t

# โหลดทันทีที่ import
_load_users()
_load_tasks()


# ── session ────────────────────────────────────────────────────────────────────
def save_session(email: str):
    with open(_SES_FILE, "w", encoding="utf-8") as f:
        json.dump({"email": email.lower().strip()}, f)

def clear_session():
    if os.path.exists(_SES_FILE):
        os.remove(_SES_FILE)

def load_session() -> tuple[str | None, str | None]:
    """คืน (username, email) ถ้ายังมี session อยู่, ไม่งั้นคืน (None, None)"""
    if not os.path.exists(_SES_FILE):
        return None, None
    try:
        with open(_SES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        email = data.get("email", "").lower().strip()
        if email in _users:
            return _users[email]["username"], email
    except Exception:
        pass
    return None, None


# ── user API ───────────────────────────────────────────────────────────────────
def register_user(username: str, email: str, password: str) -> bool:
    email = email.lower().strip()
    if email in _users:
        return False
    _users[email] = {"username": username, "password": password}
    _save_users()
    return True

def login_user(email: str, password: str) -> str | None:
    email = email.lower().strip()
    if email not in _users:
        return "not_found"
    if _users[email]["password"] != password:
        return "wrong_pass"
    save_session(email)
    return _users[email]["username"]

def email_exists(email: str) -> bool:
    return email.lower().strip() in _users

def reset_password(email: str, new_password: str) -> bool:
    email = email.lower().strip()
    if email not in _users:
        return False
    _users[email]["password"] = new_password
    _save_users()
    return True


# ── task API ───────────────────────────────────────────────────────────────────
def load_tasks(email: str) -> list[dict]:
    email = email.lower().strip()
    raw = _tasks.get(email, [])
    return [_deserialize_task(t) for t in raw]

def save_tasks(email: str, task_list: list[dict]):
    email = email.lower().strip()
    _tasks[email] = [_serialize_task(t) for t in task_list]
    _save_tasks()