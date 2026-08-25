from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt

from UI.Staff.StaffWindow import StaffWindow
from UI.Client.ClientWindow import ClientWindow


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
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(100, 60, 100, 60)
        layout.setSpacing(20)

        central_widget.setLayout(layout)

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel("Food Bank System")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        # ====================================================
        # LOGIN MESSAGE
        # ====================================================

        message = QLabel(
            "Please select how you would like to continue."
        )

        message.setAlignment(Qt.AlignCenter)

        message.setStyleSheet("""
            font-size: 17px;
        """)

        layout.addWidget(message)

        layout.addSpacing(30)

        # ====================================================
        # STAFF BUTTON
        # ====================================================

        staff_button = QPushButton("Staff Login")

        staff_button.setMinimumHeight(70)

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

        staff_button.clicked.connect(self.open_staff)

        layout.addWidget(staff_button)

        # ====================================================
        # CLIENT BUTTON
        # ====================================================

        client_button = QPushButton("Client")

        client_button.setMinimumHeight(70)

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

        client_button.clicked.connect(self.open_client)

        layout.addWidget(client_button)

        layout.addStretch()

    # ========================================================
    # OPEN STAFF WINDOW
    # ========================================================

    def open_staff(self):

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