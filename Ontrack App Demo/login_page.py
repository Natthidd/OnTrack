from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

import user_store
from styles import MAIN_STYLE, styled_msgbox


class PasswordField(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)
        self.input.setMinimumHeight(50)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setObjectName("eyeBtn")
        self.eye_btn.setFixedSize(44, 50)
        self.eye_btn.setCursor(Qt.PointingHandCursor)
        self.eye_btn.clicked.connect(self._toggle)
        self._visible = False

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1.5px solid #D0D7E2;
                border-radius: 10px;
            }
            QFrame:focus-within {
                border: 1.5px solid #1e293b;
            }
        """)
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(4, 0, 4, 0)
        c_layout.setSpacing(0)

        self.input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                padding: 12px 10px;
                font-size: 14px;
                color: #1e293b;
            }
        """)
        c_layout.addWidget(self.input)
        c_layout.addWidget(self.eye_btn)

        layout.addWidget(container)

    def _toggle(self):
        self._visible = not self._visible
        if self._visible:
            self.input.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("🙈")
        else:
            self.input.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("👁")

    def text(self):
        return self.input.text()

    def clear(self):
        self.input.clear()


class LoginPage(QWidget):
    go_to_signup = Signal()
    go_to_reset = Signal()
    login_success = Signal(str)   # send username to Task

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLE)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setMaximumWidth(420)
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 48, 32, 32)
        layout.setSpacing(0)

        title = QLabel("OnTrack")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(6)

        subtitle = QLabel("Stay on track, stay on time.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(32)

        section = QLabel("Login Here!")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        layout.addSpacing(20)

        email_lbl = QLabel("Email")
        email_lbl.setObjectName("fieldLabel")
        layout.addWidget(email_lbl)
        layout.addSpacing(6)

        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(50)
        self.email_input.setPlaceholderText("")
        layout.addWidget(self.email_input)

        layout.addSpacing(16)

        pass_lbl = QLabel("Password")
        pass_lbl.setObjectName("fieldLabel")
        layout.addWidget(pass_lbl)
        layout.addSpacing(6)

        self.pass_field = PasswordField()
        layout.addWidget(self.pass_field)

        layout.addSpacing(8)

        # Forgot password — currently on emit go_to_reset instead of popup
        forgot_row = QHBoxLayout()
        forgot_row.addStretch()
        forgot_btn = QPushButton("Forgot password?")
        forgot_btn.setObjectName("linkBtn")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.clicked.connect(self.go_to_reset.emit)
        forgot_row.addWidget(forgot_btn)
        layout.addLayout(forgot_row)

        layout.addSpacing(28)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("mainBtn")
        login_btn.setMinimumHeight(56)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self._do_login)
        layout.addWidget(login_btn)

        layout.addSpacing(20)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #D0D7E2; max-height: 1px;")
        layout.addWidget(divider)

        layout.addSpacing(16)

        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignCenter)
        no_acc = QLabel("Don't have an account?")
        no_acc.setObjectName("linkText")
        create_btn = QPushButton("Create account")
        create_btn.setObjectName("linkBtn")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.clicked.connect(self.go_to_signup.emit)
        bottom_row.addWidget(no_acc)
        bottom_row.addSpacing(4)
        bottom_row.addWidget(create_btn)
        layout.addLayout(bottom_row)

        outer.addStretch()
        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(card)
        h.addStretch()
        outer.addLayout(h)
        outer.addStretch()

    def clear_fields(self):
        self.email_input.clear()
        self.pass_field.clear()

    def _do_login(self):
        email = self.email_input.text().strip()
        password = self.pass_field.text()

        if not email or not password:
            styled_msgbox(self, "Missing Fields",
                          "Please enter both email and password.",
                          QMessageBox.Warning).exec()
            return

        result = user_store.login_user(email, password)

        if result == "not_found":
            styled_msgbox(self, "Account Not Found",
                          "This email address is not registered.\nPlease create an account first.",
                          QMessageBox.Warning).exec()
        elif result == "wrong_pass":
            styled_msgbox(self, "Incorrect Password",
                          "The password you entered is incorrect.",
                          QMessageBox.Warning).exec()
        else:
            self.clear_fields()
            self.login_success.emit(result)