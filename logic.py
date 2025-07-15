import os
import json
import secrets
import string
import pyotp
import qrcode
from cryptography.fernet import Fernet

# ------------------ File Paths ------------------

KEY_FILE = "key.key"
VAULT_FILE = "vault.json"
TOTP_SECRET_FILE = "aegis_secret.txt"

# ------------------ Encryption Key Setup ------------------

if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as f:
    key = f.read()

fernet = Fernet(key)

# ------------------ Encryption Functions ------------------

def encrypt(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt(token):
    return fernet.decrypt(token.encode()).decode()

# ------------------ Vault Management ------------------

def load_vault():
    if not os.path.exists(VAULT_FILE):
        return []
    with open(VAULT_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_vault(data):
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_password_entry(app_name, username, password, vault="Personal"):
    encrypted_password = encrypt(password)
    data = load_vault()
    data.append({
        "app_name": app_name,
        "username": username,
        "password": encrypted_password,
        "vault": vault
    })
    save_vault(data)

def get_decrypted_vault():
    data = load_vault()
    for entry in data:
        try:
            entry["password"] = decrypt(entry["password"])
        except Exception:
            entry["password"] = "Decryption Error"
    return data

# ------------------ Password Generator ------------------

def generate_password(length=16, use_symbols=True):
    characters = string.ascii_letters + string.digits
    if use_symbols:
        characters += string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

# ------------------ TOTP (MFA) Setup ------------------

def setup_totp():
    if os.path.exists(TOTP_SECRET_FILE):
        return True  # Already set up

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)

    with open(TOTP_SECRET_FILE, "w") as f:
        f.write(encrypt(secret))

    uri = totp.provisioning_uri(name="AegisVault", issuer_name="AegisVault")

    img = qrcode.make(uri)
    img.show()

    print(f"[INFO] Scan the QR code in your Authenticator app. Backup Secret: {secret}")
    return True

def totp_verify(code):
    if not os.path.exists(TOTP_SECRET_FILE):
        return False

    with open(TOTP_SECRET_FILE, "r") as f:
        secret = decrypt(f.read())

    totp = pyotp.TOTP(secret)
    return totp.verify(code)
