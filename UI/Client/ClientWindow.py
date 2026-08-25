from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt

from Database.Clients import get_client_by_number


class ClientWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Food Bank")
        self.resize(1000, 700)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(
            120,
            70,
            120,
            70
        )

        self.main_layout.setSpacing(20)

        self.main_widget.setLayout(self.main_layout)

        self.show_home()

    # ========================================================
    # CLEAR SCREEN
    # ========================================================

    def clear_screen(self):

        while self.main_layout.count():

            item = self.main_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    # ========================================================
    # HOME SCREEN
    # ========================================================

    def show_home(self):

        self.clear_screen()

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel("FOOD BANK")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
        """)

        self.main_layout.addWidget(title)

        # ====================================================
        # WELCOME
        # ====================================================

        welcome = QLabel("Welcome!")

        welcome.setAlignment(Qt.AlignCenter)

        welcome.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
        """)

        self.main_layout.addWidget(welcome)

        message = QLabel(
            "Please select an option below."
        )

        message.setAlignment(Qt.AlignCenter)

        message.setStyleSheet("""
            font-size: 18px;
            color: #666666;
            padding-bottom: 20px;
        """)

        self.main_layout.addWidget(message)

        # ====================================================
        # CHECK IN
        # ====================================================

        check_in_button = QPushButton(
            "CHECK IN"
        )

        check_in_button.setMinimumHeight(100)

        check_in_button.setStyleSheet("""
            QPushButton {
                font-size: 26px;
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #cccccc;
                padding: 15px;
            }

            QPushButton:hover {
                background-color: #3b82f6;
                color: white;
            }
        """)

        check_in_button.clicked.connect(
            self.show_check_in
        )

        self.main_layout.addWidget(
            check_in_button
        )

        self.main_layout.addStretch()

        # ====================================================
        # STAFF
        # ====================================================

        staff_button = QPushButton(
            "Staff"
        )

        staff_button.setMaximumWidth(150)

        staff_button.clicked.connect(
            self.staff_login
        )

        self.main_layout.addWidget(
            staff_button,
            alignment=Qt.AlignCenter
        )

    # ========================================================
    # CHECK IN SCREEN
    # ========================================================

    def show_check_in(self):

        self.clear_screen()

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel("CHECK IN")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        self.main_layout.addWidget(title)

        # ====================================================
        # MESSAGE
        # ====================================================

        message = QLabel(
            "Please enter your client number."
        )

        message.setAlignment(Qt.AlignCenter)

        message.setStyleSheet("""
            font-size: 20px;
            color: #666666;
        """)

        self.main_layout.addWidget(message)

        # ====================================================
        # CLIENT NUMBER
        # ====================================================

        self.client_number_input = QLineEdit()

        self.client_number_input.setPlaceholderText(
            "Client number"
        )

        self.client_number_input.setMinimumHeight(60)

        self.client_number_input.setAlignment(
            Qt.AlignCenter
        )

        self.client_number_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
            }

            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)

        self.main_layout.addWidget(
            self.client_number_input
        )

        # ====================================================
        # CONTINUE
        # ====================================================

        continue_button = QPushButton(
            "CONTINUE"
        )

        continue_button.setMinimumHeight(70)

        continue_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #3b82f6;
                color: white;
            }
        """)

        continue_button.clicked.connect(
            self.check_client
        )

        self.main_layout.addWidget(
            continue_button
        )

        # ====================================================
        # CANCEL
        # ====================================================

        cancel_button = QPushButton(
            "CANCEL"
        )

        cancel_button.setMinimumHeight(60)

        cancel_button.clicked.connect(
            self.show_home
        )

        self.main_layout.addWidget(
            cancel_button
        )

        self.main_layout.addStretch()

        self.client_number_input.setFocus()

    # ========================================================
    # LOOK UP CLIENT
    # ========================================================

    def check_client(self):

        client_number = (
            self.client_number_input.text().strip()
        )

        if not client_number:

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter your client number.",
            )

            return

        try:

            client = get_client_by_number(
                client_number
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to look up client.\n\n{error}",
            )

            return

        if not client:

            QMessageBox.warning(
                self,
                "Client Not Found",
                "We couldn't find that client number.\n\n"
                "Please check the number and try again.",
            )

            return

        self.show_client_confirmation(client)

    # ========================================================
    # CLIENT CONFIRMATION
    # ========================================================

    def show_client_confirmation(self, client):

        self.clear_screen()

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel("WELCOME")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        self.main_layout.addWidget(title)

        # ====================================================
        # CLIENT NAME
        # ====================================================

        name = QLabel(
            f"{client['first_name']} "
            f"{client['last_name']}"
        )

        name.setAlignment(Qt.AlignCenter)

        name.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            padding: 20px;
        """)

        self.main_layout.addWidget(name)

        # ====================================================
        # CONFIRMATION MESSAGE
        # ====================================================

        message = QLabel(
            "Is this you?"
        )

        message.setAlignment(Qt.AlignCenter)

        message.setStyleSheet("""
            font-size: 20px;
            color: #666666;
        """)

        self.main_layout.addWidget(message)

        self.main_layout.addSpacing(20)

        # ====================================================
        # YES
        # ====================================================

        confirm_button = QPushButton(
            "YES — CHECK ME IN"
        )

        confirm_button.setMinimumHeight(80)

        confirm_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #22c55e;
                color: white;
            }
        """)

        confirm_button.clicked.connect(
            lambda: self.client_checked_in(client)
        )

        self.main_layout.addWidget(
            confirm_button
        )

        # ====================================================
        # NO
        # ====================================================

        no_button = QPushButton(
            "NO — GO BACK"
        )

        no_button.setMinimumHeight(65)

        no_button.clicked.connect(
            self.show_check_in
        )

        self.main_layout.addWidget(
            no_button
        )

        self.main_layout.addStretch()

    # ========================================================
    # CHECKED IN
    # ========================================================

    def client_checked_in(self, client):

        self.clear_screen()

        # ====================================================
        # SUCCESS MESSAGE
        # ====================================================

        title = QLabel(
            "YOU'RE CHECKED IN!"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
        """)

        self.main_layout.addWidget(title)

        # ====================================================
        # CLIENT MESSAGE
        # ====================================================

        message = QLabel(
            f"Welcome, {client['first_name']}!\n\n"
            "Please take a seat.\n"
            "A staff member will assist you shortly."
        )

        message.setAlignment(Qt.AlignCenter)

        message.setStyleSheet("""
            font-size: 22px;
            padding: 30px;
        """)

        self.main_layout.addWidget(
            message
        )

        self.main_layout.addStretch()

        # ====================================================
        # DONE
        # ====================================================

        done_button = QPushButton(
            "DONE"
        )

        done_button.setMinimumHeight(70)

        done_button.clicked.connect(
            self.show_home
        )

        self.main_layout.addWidget(
            done_button
        )

    # ========================================================
    # STAFF LOGIN
    # ========================================================

    def staff_login(self):

        from UI.MainWindow import MainWindow

        self.login_window = MainWindow()

        self.login_window.show()

        self.close()