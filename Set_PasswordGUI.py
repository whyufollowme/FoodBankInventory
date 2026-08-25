import sys
import sqlite3
import hashlib
import secrets
from pathlib import Path
import os

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt


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
    """
    Create a secure password hash.
    """

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )

    return salt.hex() + ":" + password_hash.hex()


# ============================================================
# PASSWORD WINDOW
# ============================================================

class PasswordWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Food Bank - Set Staff Password"
        )

        self.setFixedSize(
            450,
            300
        )

        # ====================================================
        # LAYOUT
        # ====================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            40,
            30,
            40,
            30
        )

        layout.setSpacing(12)

        self.setLayout(
            layout
        )

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel(
            "Set Staff Password"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
        """)

        layout.addWidget(
            title
        )

        # ====================================================
        # MESSAGE
        # ====================================================

        message = QLabel(
            "Enter the password staff will use\n"
            "to access the Staff side of the system."
        )

        message.setAlignment(
            Qt.AlignCenter
        )

        message.setStyleSheet("""
            font-size: 14px;
            margin-bottom: 10px;
        """)

        layout.addWidget(
            message
        )

        # ====================================================
        # PASSWORD
        # ====================================================

        self.password_input = QLineEdit()

        self.password_input.setPlaceholderText(
            "Enter password"
        )

        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        layout.addWidget(
            self.password_input
        )

        # ====================================================
        # CONFIRM PASSWORD
        # ====================================================

        self.confirm_input = QLineEdit()

        self.confirm_input.setPlaceholderText(
            "Confirm password"
        )

        self.confirm_input.setEchoMode(
            QLineEdit.Password
        )

        layout.addWidget(
            self.confirm_input
        )

        # ====================================================
        # SET PASSWORD BUTTON
        # ====================================================

        self.set_button = QPushButton(
            "Set Password"
        )

        self.set_button.setMinimumHeight(
            45
        )

        self.set_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #f97316;
            }
        """)

        self.set_button.clicked.connect(
            self.set_password
        )

        layout.addWidget(
            self.set_button
        )

        layout.addStretch()

        # Press Enter to set password
        self.confirm_input.returnPressed.connect(
            self.set_password
        )

        self.password_input.setFocus()

    # ========================================================
    # SET PASSWORD
    # ========================================================

    def set_password(self):

        password = self.password_input.text()
        confirm = self.confirm_input.text()

        # ====================================================
        # EMPTY PASSWORD
        # ====================================================

        if not password:

            QMessageBox.warning(
                self,
                "Password Required",
                "Please enter a password."
            )

            self.password_input.setFocus()

            return

        # ====================================================
        # PASSWORD MATCH
        # ====================================================

        if password != confirm:

            QMessageBox.warning(
                self,
                "Passwords Do Not Match",
                "The two passwords do not match."
            )

            self.confirm_input.clear()
            self.confirm_input.setFocus()

            return

        # ====================================================
        # PASSWORD LENGTH
        # ====================================================

        if len(password) < 6:

            QMessageBox.warning(
                self,
                "Password Too Short",
                "The password must be at least 6 characters long."
            )

            self.password_input.setFocus()

            return

        # ====================================================
        # CREATE DATABASE DIRECTORY
        # ====================================================

        try:

            DATA_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

        except OSError as error:

            QMessageBox.critical(
                self,
                "Error",
                "Unable to create the application data folder.\n\n"
                f"{error}"
            )

            return

        # ====================================================
        # SAVE PASSWORD
        # ====================================================

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

            QMessageBox.critical(
                self,
                "Database Error",
                "Unable to save the staff password.\n\n"
                f"{error}"
            )

            return

        # ====================================================
        # SUCCESS
        # ====================================================

        QMessageBox.information(
            self,
            "Password Set",
            "The staff password has been set successfully."
        )

        # Clear fields
        self.password_input.clear()
        self.confirm_input.clear()

        self.password_input.setFocus()


# ============================================================
# APPLICATION
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = PasswordWindow()

    window.show()

    sys.exit(
        app.exec()
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
