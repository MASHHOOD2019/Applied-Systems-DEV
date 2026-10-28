"""Secure Local Vault — encrypted credential store (CLI).

Usage:
    python vault.py init                 # create vault, set master password
    python vault.py add github           # store an entry (prompts for details)
    python vault.py get github           # show one entry
    python vault.py list                 # list entry names (not secrets)
    python vault.py delete github        # remove an entry

Everything is encrypted locally with a key derived from your master
password. Nothing leaves your machine and no password is ever stored.
"""

import argparse
import getpass
import secrets
import string
import sys

import crypto_utils


def generate_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def cmd_init(_args) -> None:
    password = getpass.getpass("Choose a master password: ")
    confirm = getpass.getpass("Confirm master password: ")
    if password != confirm:
        print("Passwords do not match.")
        sys.exit(1)
    try:
        crypto_utils.create_vault(password)
    except FileExistsError as e:
        print(e)
        sys.exit(1)
    print("Vault created. Keep your master password safe — it cannot be recovered.")


def _ask_master_password() -> str:
    return getpass.getpass("Master password: ")


def cmd_add(args) -> None:
    password = _ask_master_password()
    try:
        entries = crypto_utils.load_vault(password)
    except (ValueError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)
    username = input("Username/email: ").strip()
    choice = input("Password (leave blank to auto-generate): ").strip()
    secret = choice or generate_password()
    notes = input("Notes (optional): ").strip()
    entries[args.name] = {"username": username, "password": secret, "notes": notes}
    crypto_utils.save_vault(password, entries)
    print(f"Saved entry '{args.name}'." + (" (auto-generated password)" if not choice else ""))


def cmd_get(args) -> None:
    password = _ask_master_password()
    try:
        entries = crypto_utils.load_vault(password)
    except (ValueError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)
    entry = entries.get(args.name)
    if not entry:
        print(f"No entry named '{args.name}'.")
        sys.exit(1)
    print(f"Username: {entry['username']}")
    print(f"Password: {entry['password']}")
    if entry["notes"]:
        print(f"Notes: {entry['notes']}")


def cmd_list(_args) -> None:
    password = _ask_master_password()
    try:
        entries = crypto_utils.load_vault(password)
    except (ValueError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)
    if not entries:
        print("Vault is empty.")
        return
    print(f"{len(entries)} entr{'y' if len(entries) == 1 else 'ies'}:")
    for name in sorted(entries):
        print(f"  - {name}")


def cmd_delete(args) -> None:
    password = _ask_master_password()
    try:
        entries = crypto_utils.load_vault(password)
    except (ValueError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)
    if args.name not in entries:
        print(f"No entry named '{args.name}'.")
        sys.exit(1)
    del entries[args.name]
    crypto_utils.save_vault(password, entries)
    print(f"Deleted '{args.name}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Secure Local Vault")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    add_p = sub.add_parser("add")
    add_p.add_argument("name")
    get_p = sub.add_parser("get")
    get_p.add_argument("name")
    sub.add_parser("list")
    del_p = sub.add_parser("delete")
    del_p.add_argument("name")
    args = parser.parse_args()
    {"init": cmd_init, "add": cmd_add, "get": cmd_get,
     "list": cmd_list, "delete": cmd_delete}[args.command](args)


if __name__ == "__main__":
    main()
