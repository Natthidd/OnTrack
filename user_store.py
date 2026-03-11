_users = {}  # email -> {"username": str, "password": str}

def register_user(username: str, email: str, password: str) -> bool:
    """Register a new user. Returns False if email already exists."""
    email = email.lower().strip()
    if email in _users:
        return False
    _users[email] = {"username": username, "password": password}
    return True


def login_user(email: str, password: str) -> str | None:
    """
    Attempt login. Returns:
      - "not_found"   if email is not registered
      - "wrong_pass"  if password doesn't match
      - username      on success
    """
    email = email.lower().strip()
    if email not in _users:
        return "not_found"
    if _users[email]["password"] != password:
        return "wrong_pass"
    return _users[email]["username"]


def email_exists(email: str) -> bool:
    return email.lower().strip() in _users
