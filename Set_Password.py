import sqlite3
import hashlib
import secrets
from pathlib import Path
import os
import getpass


# ============================================================
# DATABASE LOCATION
# ============================================================

APP_DATA_DIR = Path(
    os.environ.get("LOCALAPPDATA", Path.home())
) / "Food Bank"

DATA_DIR = APP_DATA_DIR / "data"
DATABASE_PATH = DATA_DIR / "foodbank.db"


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )

    return salt.hex() + ":" + password_hash.hex()


# ============================================================
# SETUP
# ============================================================

print()
print("===================================")
print("       FOOD BANK STAFF SETUP")
print("===================================")
print()

# Make sure the database directory exists
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ------------------------------------------------------------
# Get password
# ------------------------------------------------------------

while True:

    password = getpass.getpass(
        "Enter the staff password: "
    )

    if not password:
        print("Password cannot be empty.")
        print()
        continue

    confirm = getpass.getpass(
        "Enter the password again: "
    )

    if password != confirm:

        print()
        print("Passwords do not match.")
        print()

        continue

    break


# ============================================================
# SAVE PASSWORD
# ============================================================

try:

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    # Make sure settings table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    password_hash = hash_password(
        password
    )

    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES ('staff_password', ?)

        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (password_hash,))

    connection.commit()
    connection.close()

except sqlite3.Error as error:

    print()
    print("ERROR: Could not save the password.")
    print()
    print(error)

    input("\nPress Enter to exit...")
    raise SystemExit


# ============================================================
# DONE
# ============================================================

print()
print("===================================")
print("       PASSWORD SET SUCCESSFULLY")
print("===================================")
print()
print("The staff password has been saved.")
print()
print("You can now start the Food Bank System.")
print()

input("Press Enter to exit...")