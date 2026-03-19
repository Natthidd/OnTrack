import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QFont

from login_page import LoginPage
from signup_page import SignUpPage
from reset_password_page import ResetPasswordPage
from mytask_page import TaskPage
from styles import BG_COLOR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnTrack")
        self.setMinimumSize(480, 700)
        self.resize(480, 780)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page  = LoginPage()
        self.signup_page = SignUpPage()
        self.reset_page  = ResetPasswordPage()
        self.task_page   = TaskPage()

        self.stack.addWidget(self.login_page)   # 0
        self.stack.addWidget(self.signup_page)  # 1
        self.stack.addWidget(self.reset_page)   # 2
        self.stack.addWidget(self.task_page)    # 3

        self.login_page.go_to_signup.connect(self._show_signup)
        self.login_page.go_to_reset.connect(self._show_reset)
        self.login_page.login_success.connect(self._show_task)
        self.signup_page.go_to_login.connect(self._show_login)
        self.reset_page.go_to_login.connect(self._show_login)
        self.task_page.go_to_login.connect(self._show_login)

        self.stack.setCurrentIndex(0)

    def _show_signup(self):
        self.stack.setCurrentIndex(1)

    def _show_login(self):
        self.login_page.clear_fields()
        self.stack.setCurrentIndex(0)

    def _show_reset(self):
        self.stack.setCurrentIndex(2)

    def _show_task(self, username: str):
        self.task_page.set_username(username)
        self.stack.setCurrentIndex(3)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()