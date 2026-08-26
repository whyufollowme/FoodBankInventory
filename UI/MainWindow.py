import sqlite3
import hashlib
import secrets
from pathlib import Path
import os

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
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
# FOOD BANK INVENTORY SYSTEM
# VERSION 1.3.0
# ============================================================


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
        self.setFixedSize(420, 270)

        # ====================================================
        # MAIN LAYOUT
        # ====================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(15)

        self.setLayout(layout)

        # ====================================================
        # DARK THEME
        # ====================================================

        self.setStyleSheet("""
            QDialog {
                background-color: #171a1f;
            }

            QLabel {
                color: #f3f4f6;
            }

            QLineEdit {
                background-color: #22262d;
                color: #f3f4f6;
                border: 2px solid #343a43;
                border-radius: 9px;
                padding: 11px;
                font-size: 15px;
                selection-background-color: #f97316;
            }

            QLineEdit:focus {
                border: 2px solid #f97316;
            }

            QDialogButtonBox {
                background-color: transparent;
            }

            QPushButton {
                background-color: #f97316;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #ea580c;
            }

            QPushButton:pressed {
                background-color: #c2410c;
            }
        """)

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel(
            "🔐  Staff Login"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            QLabel {
                font-size: 25px;
                font-weight: 800;
                color: #f3f4f6;
                margin-bottom: 5px;
            }
        """)

        layout.addWidget(
            title
        )

        # ====================================================
        # DESCRIPTION
        # ====================================================

        description = QLabel(
            "Enter the staff password to access\n"
            "the management system."
        )

        description.setAlignment(
            Qt.AlignCenter
        )

        description.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #9ca3af;
            }
        """)

        layout.addWidget(
            description
        )

        # ====================================================
        # PASSWORD
        # ====================================================

        self.password_input = QLineEdit()

        self.password_input.setPlaceholderText(
            "Enter staff password"
        )

        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        layout.addWidget(
            self.password_input
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            self.login
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(
            buttons
        )

        # ====================================================
        # ENTER KEY
        # ====================================================

        self.password_input.returnPressed.connect(
            self.login
        )

        self.password_input.setFocus()

    # ========================================================
    # LOGIN
    # ========================================================

    def login(self):

        password = self.password_input.text()

        # ====================================================
        # EMPTY PASSWORD
        # ====================================================

        if not password:

            QMessageBox.warning(
                self,
                "Password Required",
                "Please enter the staff password."
            )

            return

        # ====================================================
        # DATABASE CONNECTION
        # ====================================================

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

        # ====================================================
        # WINDOW SETTINGS
        # ====================================================

        self.setWindowTitle(
            "Food Bank Inventory System"
        )

        self.resize(
            1100,
            700
        )

        self.setMinimumSize(
            900,
            600
        )

        self.staff_window = None
        self.client_window = None

        # ====================================================
        # CENTRAL WIDGET
        # ====================================================

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        # ====================================================
        # MAIN LAYOUT
        # ====================================================

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            70,
            45,
            70,
            30
        )

        main_layout.setSpacing(0)

        central_widget.setLayout(
            main_layout
        )

        # ====================================================
        # DARK BACKGROUND
        # ====================================================

        central_widget.setStyleSheet("""
            QWidget {
                background-color: #111418;
                color: #f3f4f6;
            }
        """)

        # ====================================================
        # HEADER
        # ====================================================

        header_layout = QVBoxLayout()

        header_layout.setSpacing(4)

        # ====================================================
        # MAIN TITLE
        # ====================================================

        title = QLabel(
            "FOOD BANK"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            QLabel {
                font-size: 40px;
                font-weight: 800;
                color: #f3f4f6;
                letter-spacing: 3px;
            }
        """)

        header_layout.addWidget(
            title
        )

        # ====================================================
        # SYSTEM TITLE
        # ====================================================

        subtitle = QLabel(
            "INVENTORY SYSTEM"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setStyleSheet("""
            QLabel {
                font-size: 19px;
                font-weight: 700;
                color: #f97316;
                letter-spacing: 5px;
            }
        """)

        header_layout.addWidget(
            subtitle
        )

        # ====================================================
        # DESCRIPTION
        # ====================================================

        description = QLabel(
            "Community food bank management platform"
        )

        description.setAlignment(
            Qt.AlignCenter
        )

        description.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #9ca3af;
                margin-top: 8px;
            }
        """)

        header_layout.addWidget(
            description
        )

        main_layout.addLayout(
            header_layout
        )

        # ====================================================
        # DIVIDER
        # ====================================================

        divider = QWidget()

        divider.setFixedHeight(
            2
        )

        divider.setStyleSheet("""
            background-color: #272c33;
            margin-top: 30px;
            margin-bottom: 25px;
        """)

        main_layout.addWidget(
            divider
        )

        # ====================================================
        # WELCOME MESSAGE
        # ====================================================

        welcome = QLabel(
            "How would you like to continue?"
        )

        welcome.setAlignment(
            Qt.AlignCenter
        )

        welcome.setStyleSheet("""
            QLabel {
                font-size: 23px;
                font-weight: 700;
                color: #e5e7eb;
                margin-bottom: 25px;
            }
        """)

        main_layout.addWidget(
            welcome
        )

        # ====================================================
        # CARDS LAYOUT
        # ====================================================

        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(
            25
        )

        # ====================================================
        # CLIENT CARD
        # ====================================================

        client_card = QWidget()

        client_card.setObjectName(
            "clientCard"
        )

        client_card.setMinimumHeight(
            320
        )

        client_card.setStyleSheet("""
            QWidget#clientCard {
                background-color: #1b2026;
                border: 2px solid #292f37;
                border-radius: 18px;
            }

            QWidget#clientCard:hover {
                border: 2px solid #2563eb;
                background-color: #1d232b;
            }
        """)

        client_layout = QVBoxLayout()

        client_layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        client_layout.setSpacing(
            12
        )

        client_card.setLayout(
            client_layout
        )

        # ====================================================
        # CLIENT ICON
        # ====================================================

        client_icon = QLabel(
            "👤"
        )

        client_icon.setAlignment(
            Qt.AlignCenter
        )

        client_icon.setStyleSheet("""
            QLabel {
                font-size: 50px;
                border: none;
                background: transparent;
            }
        """)

        client_layout.addWidget(
            client_icon
        )

        # ====================================================
        # CLIENT TITLE
        # ====================================================

        client_title = QLabel(
            "CLIENT"
        )

        client_title.setAlignment(
            Qt.AlignCenter
        )

        client_title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: 800;
                color: #60a5fa;
                border: none;
                background: transparent;
            }
        """)

        client_layout.addWidget(
            client_title
        )

        # ====================================================
        # CLIENT DESCRIPTION
        # ====================================================

        client_description = QLabel(
            "Access food bank services\n"
            "and client information."
        )

        client_description.setAlignment(
            Qt.AlignCenter
        )

        client_description.setWordWrap(
            True
        )

        client_description.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #9ca3af;
                border: none;
                background: transparent;
            }
        """)

        client_layout.addWidget(
            client_description
        )

        client_layout.addStretch()

        # ====================================================
        # CLIENT BUTTON
        # ====================================================

        client_button = QPushButton(
            "CONTINUE  →"
        )

        client_button.setCursor(
            Qt.PointingHandCursor
        )

        client_button.setMinimumHeight(
            52
        )

        client_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #3b82f6;
            }

            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)

        client_button.clicked.connect(
            self.open_client
        )

        client_layout.addWidget(
            client_button
        )

        cards_layout.addWidget(
            client_card
        )

        # ====================================================
        # STAFF CARD
        # ====================================================

        staff_card = QWidget()

        staff_card.setObjectName(
            "staffCard"
        )

        staff_card.setMinimumHeight(
            320
        )

        staff_card.setStyleSheet("""
            QWidget#staffCard {
                background-color: #1b2026;
                border: 2px solid #292f37;
                border-radius: 18px;
            }

            QWidget#staffCard:hover {
                border: 2px solid #f97316;
                background-color: #211f1c;
            }
        """)

        staff_layout = QVBoxLayout()

        staff_layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        staff_layout.setSpacing(
            12
        )

        staff_card.setLayout(
            staff_layout
        )

        # ====================================================
        # STAFF ICON
        # ====================================================

        staff_icon = QLabel(
            "🔐"
        )

        staff_icon.setAlignment(
            Qt.AlignCenter
        )

        staff_icon.setStyleSheet("""
            QLabel {
                font-size: 50px;
                border: none;
                background: transparent;
            }
        """)

        staff_layout.addWidget(
            staff_icon
        )

        # ====================================================
        # STAFF TITLE
        # ====================================================

        staff_title = QLabel(
            "STAFF PORTAL"
        )

        staff_title.setAlignment(
            Qt.AlignCenter
        )

        staff_title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: 800;
                color: #fb923c;
                border: none;
                background: transparent;
            }
        """)

        staff_layout.addWidget(
            staff_title
        )

        # ====================================================
        # STAFF DESCRIPTION
        # ====================================================

        staff_description = QLabel(
            "Manage inventory, clients,\n"
            "and food bank operations."
        )

        staff_description.setAlignment(
            Qt.AlignCenter
        )

        staff_description.setWordWrap(
            True
        )

        staff_description.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #9ca3af;
                border: none;
                background: transparent;
            }
        """)

        staff_layout.addWidget(
            staff_description
        )

        staff_layout.addStretch()

        # ====================================================
        # STAFF BUTTON
        # ====================================================

        staff_button = QPushButton(
            "STAFF LOGIN  →"
        )

        staff_button.setCursor(
            Qt.PointingHandCursor
        )

        staff_button.setMinimumHeight(
            52
        )

        staff_button.setStyleSheet("""
            QPushButton {
                background-color: #f97316;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #fb923c;
            }

            QPushButton:pressed {
                background-color: #ea580c;
            }
        """)

        staff_button.clicked.connect(
            self.open_staff
        )

        staff_layout.addWidget(
            staff_button
        )

        cards_layout.addWidget(
            staff_card
        )

        # ====================================================
        # ADD CARDS TO MAIN LAYOUT
        # ====================================================

        main_layout.addLayout(
            cards_layout
        )

        # ====================================================
        # FOOTER
        # ====================================================

        main_layout.addStretch()

        footer = QLabel(
            "Food Bank Inventory System  •  Version 1.3.0"
        )

        footer.setAlignment(
            Qt.AlignCenter
        )

        footer.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6b7280;
                margin-top: 20px;
            }
        """)

        main_layout.addWidget(
            footer
        )

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