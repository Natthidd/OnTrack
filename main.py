
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from login_page import LoginPage
from signup_page import SignUpPage
from styles import BG_COLOR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnTrack")
        self.setMinimumSize(480, 700)
        self.resize(480, 780)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        # Stacked widget to switch pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages
        self.login_page = LoginPage()
        self.signup_page = SignUpPage()

        self.stack.addWidget(self.login_page)   # index 0
        self.stack.addWidget(self.signup_page)  # index 1

        # Connect signals
        self.login_page.go_to_signup.connect(self._show_signup)
        self.signup_page.go_to_login.connect(self._show_login)

        # Start at login
        self.stack.setCurrentIndex(0)

    def _show_signup(self):
        self.stack.setCurrentIndex(1)

    def _show_login(self):
        self.login_page.clear_fields()
        self.stack.setCurrentIndex(0)


def main():
    app = QApplication(sys.argv)

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
