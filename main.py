import sys

from PySide6.QtWidgets import QApplication

from Database.Database import initialize_database
from UI.MainWindow import MainWindow


def main():

    # Initialize database
    initialize_database()

    # Start Qt
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow()

    # Show window
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()