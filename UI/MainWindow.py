import sqlite3
import hashlib
import secrets
from pathlib import Path
import os

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)
from PySide6.QtCore import Qt

from UI.Staff.StaffWindow import StaffWindow
from UI.Client.ClientWindow import ClientWindow


# ============================================================
# DATABASE LOCATION
# ============================================================

APP_DATA_DIR = Path(
    os.environ.get("LOCALAPPDATA", Path.home())
) / "Food Bank"

DATABASE_PATH = APP_DATA_DIR / "data" / "foodbank.db"


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password):
    """Create a secure password hash."""

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )

    return salt.hex() + ":" + password_hash.hex()


def verify_password(password, stored_hash):
    """Verify a password against its stored hash."""

    try:
        salt_hex, hash_hex = stored_hash.split(":")

        salt = bytes.fromhex(salt_hex)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100000
        )

        return secrets.compare_digest(
            password_hash.hex(),
            hash_hex
        )

    except (ValueError, TypeError):
        return False


# ============================================================
# STAFF LOGIN DIALOG
# ============================================================

class StaffLoginDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Staff Login")
        self.setFixedWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel("Staff Login")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
        """)

        layout.addWidget(title)

        # ====================================================
        # PASSWORD
        # ====================================================

        self.password_input = QLineEdit()

        self.password_input.setPlaceholderText("Enter staff password")

        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        layout.addWidget(self.password_input)

        # ====================================================
        # BUTTONS
        # ====================================================

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.login)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.password_input.returnPressed.connect(
            self.login
        )

        self.password_input.setFocus()

    # ========================================================
    # LOGIN
    # ========================================================

    def login(self):

        password = self.password_input.text()

        if not password:

            QMessageBox.warning(
                self,
                "Password Required",
                "Please enter the staff password."
            )

            return

        try:

            connection = sqlite3.connect(
                DATABASE_PATH
            )

            cursor = connection.cursor()

            cursor.execute("""
                SELECT value
                FROM settings
                WHERE key = 'staff_password'
            """)

            result = cursor.fetchone()

            connection.close()

        except sqlite3.Error as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to access the database.\n\n{error}"
            )

            return

        # ====================================================
        # PASSWORD NOT SET
        # ====================================================

        if result is None:

            QMessageBox.critical(
                self,
                "Staff Password Not Set",
                "The staff password has not been configured yet."
            )

            return

        stored_hash = result[0]

        # ====================================================
        # VERIFY PASSWORD
        # ====================================================

        if verify_password(
            password,
            stored_hash
        ):

            self.accept()

        else:

            QMessageBox.warning(
                self,
                "Login Failed",
                "Incorrect staff password."
            )

            self.password_input.clear()
            self.password_input.setFocus()


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Food Bank System")
        self.resize(900, 600)

        self.staff_window = None
        self.client_window = None

        # ====================================================
        # MAIN WIDGET
        # ====================================================

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            100,
            60,
            100,
            60
        )

        layout.setSpacing(20)

        central_widget.setLayout(
            layout
        )

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel(
            "Food Bank System"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addWidget(
            title
        )

        # ====================================================
        # LOGIN MESSAGE
        # ====================================================

        message = QLabel(
            "Please select how you would like to continue."
        )

        message.setAlignment(
            Qt.AlignCenter
        )

        message.setStyleSheet("""
            font-size: 17px;
        """)

        layout.addWidget(
            message
        )

        layout.addSpacing(30)

        # ====================================================
        # STAFF BUTTON
        # ====================================================

        staff_button = QPushButton(
            "Staff Login"
        )

        staff_button.setMinimumHeight(
            70
        )

        staff_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                border-radius: 8px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #f97316;
            }
        """)

        staff_button.clicked.connect(
            self.open_staff
        )

        layout.addWidget(
            staff_button
        )

        # ====================================================
        # CLIENT BUTTON
        # ====================================================

        client_button = QPushButton(
            "Client"
        )

        client_button.setMinimumHeight(
            70
        )

        client_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                border-radius: 8px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #f97316;
            }
        """)

        client_button.clicked.connect(
            self.open_client
        )

        layout.addWidget(
            client_button
        )

        layout.addStretch()

    # ========================================================
    # OPEN STAFF WINDOW
    # ========================================================

    def open_staff(self):

        login = StaffLoginDialog(
            self
        )

        result = login.exec()

        # Password was incorrect or Cancel was pressed
        if result != QDialog.Accepted:
            return

        # ====================================================
        # PASSWORD CORRECT
        # ====================================================

        self.staff_window = StaffWindow()

        self.staff_window.show()

        self.close()

    # ========================================================
    # OPEN CLIENT WINDOW
    # ========================================================

    def open_client(self):

        self.client_window = ClientWindow()

        self.client_window.show()

        self.close()