import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QFont, QPixmap

from login_page import LoginPage
from signup_page import SignUpPage
from reset_password_page import ResetPasswordPage
from mytask_page import TaskPage
from profile_page import ProfilePage
from edit_profile_page import EditProfilePage
from graph_page import GraphPage
from styles import BG_COLOR
import user_store


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnTrack")
        self.setMinimumSize(480, 700)
        self.resize(480, 780)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page       = LoginPage()
        self.signup_page      = SignUpPage()
        self.reset_page       = ResetPasswordPage()
        self.task_page        = TaskPage()
        self.profile_page     = ProfilePage()
        self.edit_profile_page = EditProfilePage()
        self.graph_page       = GraphPage()

        self.stack.addWidget(self.login_page)         # 0
        self.stack.addWidget(self.signup_page)        # 1
        self.stack.addWidget(self.reset_page)         # 2
        self.stack.addWidget(self.task_page)          # 3
        self.stack.addWidget(self.profile_page)       # 4
        self.stack.addWidget(self.edit_profile_page)  # 5
        self.stack.addWidget(self.graph_page)         # 6

        # signals
        self.login_page.go_to_signup.connect(self._show_signup)
        self.login_page.go_to_reset.connect(self._show_reset)
        self.login_page.login_success.connect(self._show_task)

        self.signup_page.go_to_login.connect(self._show_login)
        self.reset_page.go_to_login.connect(self._show_login)

        self.task_page.go_to_login.connect(self._show_login)
        self.task_page.go_to_profile.connect(self._show_profile)
        self.task_page.go_to_graph.connect(self._show_graph)

        self.graph_page.go_to_task.connect(self._show_task_page)

        self.profile_page.go_to_task.connect(self._show_task_page)
        self.profile_page.go_to_edit_profile.connect(self._show_edit_profile)

        self.edit_profile_page.go_to_profile.connect(self._show_profile)
        self.edit_profile_page.profile_updated.connect(self._on_profile_updated)

        # session restore
        saved_username, saved_email = user_store.load_session()
        if saved_username and saved_email:
            self._show_task(saved_username, saved_email)
        else:
            self.stack.setCurrentIndex(0)

    # ── navigation ────────────────────────────────────────────
    def _show_signup(self):
        self.stack.setCurrentIndex(1)

    def _show_login(self):
        user_store.clear_session()
        self.login_page.clear_fields()
        self.stack.setCurrentIndex(0)

    def _show_reset(self):
        self.stack.setCurrentIndex(2)

    def _show_task(self, username: str, email: str = ""):
        if not email:
            _, email = user_store.load_session()
            if not email:
                for e, d in user_store._users.items():
                    if d["username"] == username:
                        email = e
                        break
        self._current_username = username
        self._current_email    = email

        # โหลด avatar จาก path ที่บันทึกไว้
        saved_path = user_store.load_avatar_path(email)
        if saved_path and os.path.exists(saved_path):
            from PySide6.QtGui import QPixmap as _QPixmap
            px = _QPixmap(saved_path)
            if not px.isNull():
                self._current_avatar = px

        self.task_page.set_user(username, email)
        self.task_page.set_avatar(self._get_current_avatar())
        self.stack.setCurrentIndex(3)

    def _show_graph(self):
        self.graph_page.set_user(self._current_email)
        self.stack.setCurrentIndex(6)

    def _show_task_page(self):
        self.stack.setCurrentIndex(3)

    def _show_profile(self):
        self.profile_page.set_user(self._current_username, self._current_email)
        # sync avatar
        avatar = self._get_current_avatar()
        self.profile_page.set_avatar(avatar)
        self.stack.setCurrentIndex(4)

    def _show_edit_profile(self):
        avatar = self._get_current_avatar()
        self.edit_profile_page.set_user(
            self._current_username, self._current_email, avatar
        )
        self.stack.setCurrentIndex(5)

    def _on_profile_updated(self, new_username: str, new_avatar):
        """รับข้อมูลที่แก้ไขจาก EditProfilePage แล้ว sync ทุกหน้า"""
        self._current_username = new_username
        # อัพเดต avatar ถ้ามี
        if new_avatar is not None:
            self._current_avatar = new_avatar
        # sync task page
        self.task_page.set_username(new_username)
        self.task_page.set_avatar(self._get_current_avatar())
        # sync profile page (จะถูกเรียกผ่าน _show_profile อีกที)

    def _get_current_avatar(self) -> QPixmap | None:
        return getattr(self, "_current_avatar", None)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()