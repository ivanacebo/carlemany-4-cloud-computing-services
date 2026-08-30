from hashlib import sha256


def hash_password(username: str, password: str) -> str:
    return sha256((username + password).encode()).hexdigest()
