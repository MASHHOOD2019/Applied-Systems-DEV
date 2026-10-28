"""Encryption layer for the vault.

Security design:
- The master password is NEVER stored. A key is derived from it with
  PBKDF2-HMAC-SHA256 (600,000 iterations) and a random 16-byte salt.
- Entry data is encrypted with Fernet (AES-128-CBC + HMAC, via the
  `cryptography` package) using that derived key.
- A wrong master password fails decryption (InvalidToken) — that is
  how the vault knows the password is wrong, without storing a hash
  to attack offline.
"""

import base64
import json
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_FILE = os.path.expanduser("~/.secure-vault.json")
ITERATIONS = 600_000


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def create_vault(password: str) -> None:
    """Create a new empty vault. Refuses to overwrite an existing one."""
    if os.path.exists(VAULT_FILE):
        raise FileExistsError("Vault already exists. Delete it first to start over.")
    salt = os.urandom(16)
    fernet = Fernet(_derive_key(password, salt))
    blob = fernet.encrypt(json.dumps({}).encode())
    with open(VAULT_FILE, "w") as f:
        json.dump({
            "salt": base64.b64encode(salt).decode(),
            "data": blob.decode(),
        }, f)
    os.chmod(VAULT_FILE, 0o600)  # owner read/write only


def load_vault(password: str) -> dict:
    """Decrypt and return all entries. Raises ValueError on wrong password."""
    if not os.path.exists(VAULT_FILE):
        raise FileNotFoundError("No vault found. Run `vault.py init` first.")
    with open(VAULT_FILE) as f:
        stored = json.load(f)
    salt = base64.b64decode(stored["salt"])
    fernet = Fernet(_derive_key(password, salt))
    try:
        plaintext = fernet.decrypt(stored["data"].encode())
    except InvalidToken:
        raise ValueError("Wrong master password.")
    return json.loads(plaintext)


def save_vault(password: str, entries: dict) -> None:
    with open(VAULT_FILE) as f:
        stored = json.load(f)
    salt = base64.b64decode(stored["salt"])
    fernet = Fernet(_derive_key(password, salt))
    blob = fernet.encrypt(json.dumps(entries).encode())
    with open(VAULT_FILE, "w") as f:
        json.dump({"salt": stored["salt"], "data": blob.decode()}, f)
