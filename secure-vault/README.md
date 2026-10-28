# Secure Local Vault

Encrypted credential store that runs entirely on your own machine —
no cloud account, no server, nothing leaves the device. The kind of
secure-local-storage tooling valued in industrial and plant environments,
where sensitive data must stay offline.

## Security design
- **Master password is never stored.** A key is derived from it with
  PBKDF2-HMAC-SHA256 (600,000 iterations) and a random salt.
- **AES + HMAC encryption** via Fernet (from the `cryptography` package).
- **Wrong password = failed decryption.** There is no password hash in
  the file to attack; the encrypted blob itself is the check.
- **File permissions** set to owner-only (`0600`) on creation.
- **Passwords are never passed as arguments** — they are read with
  `getpass`, so they don't appear in shell history.

## Run it
```bash
pip install -r requirements.txt
python vault.py init
python vault.py add github
python vault.py get github
python vault.py list
python vault.py delete github
```

## What it demonstrates
- Applied cryptography (KDF, symmetric encryption, salt handling)
- Secure CLI design (getpass, secrets module, file permissions)
- Threat modelling: what is stored, what is not, and why
