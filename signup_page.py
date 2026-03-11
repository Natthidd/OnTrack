from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

import user_store
from styles import MAIN_STYLE


class PasswordField(QWidget):
    """Reusable password input with show/hide toggle."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1.5px solid #D0D7E2;
                border-radius: 10px;
            }
            QFrame:focus-within {
                border: 1.5px solid #1C2333;
            }
        """)
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(4, 0, 4, 0)
        c_layout.setSpacing(0)

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)
        self.input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                padding: 12px 10px;
                font-size: 14px;
                color: #1C2333;
            }
        """)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setObjectName("eyeBtn")
        self.eye_btn.setFixedSize(44, 50)
        self.eye_btn.setCursor(Qt.PointingHandCursor)
        self.eye_btn.clicked.connect(self._toggle)
        self._visible = False

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


class SignUpPage(QWidget):
    go_to_login = Signal()

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

        # Header
        title = QLabel("Welcome!")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(6)

        subtitle = QLabel("Create an account to join OnTrack")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(32)

        # Section title
        section = QLabel("Sign Up")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        layout.addSpacing(20)

        # Username
        un_lbl = QLabel("Username")
        un_lbl.setObjectName("fieldLabel")
        layout.addWidget(un_lbl)
        layout.addSpacing(6)

        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(50)
        layout.addWidget(self.username_input)

        layout.addSpacing(16)

        # Email
        em_lbl = QLabel("Email Address")
        em_lbl.setObjectName("fieldLabel")
        layout.addWidget(em_lbl)
        layout.addSpacing(6)

        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(50)
        layout.addWidget(self.email_input)

        layout.addSpacing(16)

        # Password
        pw_lbl = QLabel("Password")
        pw_lbl.setObjectName("fieldLabel")
        layout.addWidget(pw_lbl)
        layout.addSpacing(6)

        self.pass_field = PasswordField()
        layout.addWidget(self.pass_field)

        layout.addSpacing(6)

        hint = QLabel("Use 8 or more characters with a mix of letters, number & symbols.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addSpacing(16)

        # Confirm Password
        cp_lbl = QLabel("Confirm Password")
        cp_lbl.setObjectName("fieldLabel")
        layout.addWidget(cp_lbl)
        layout.addSpacing(6)

        self.confirm_field = PasswordField()
        layout.addWidget(self.confirm_field)

        layout.addSpacing(32)

        # Sign Up button
        signup_btn = QPushButton("Sign Up")
        signup_btn.setObjectName("mainBtn")
        signup_btn.setMinimumHeight(56)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.clicked.connect(self._do_signup)
        layout.addWidget(signup_btn)

        layout.addSpacing(16)

        # Already have account row
        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignCenter)
        already = QLabel("Already have an account?")
        already.setObjectName("linkText")
        login_btn = QPushButton("Login")
        login_btn.setObjectName("linkBtn")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.go_to_login.emit)
        bottom_row.addWidget(already)
        bottom_row.addSpacing(4)
        bottom_row.addWidget(login_btn)
        layout.addLayout(bottom_row)

        # Center
        outer.addStretch()
        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(card)
        h.addStretch()
        outer.addLayout(h)
        outer.addStretch()

    def clear_fields(self):
        self.username_input.clear()
        self.email_input.clear()
        self.pass_field.clear()
        self.confirm_field.clear()

    def _do_signup(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_field.text()
        confirm = self.confirm_field.text()

        # Validation
        if not username or not email or not password or not confirm:
            QMessageBox.warning(self, "Missing Fields", "Please fill in all fields.")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Weak Password",
                                "Password must be at least 8 characters long.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch",
                                "Passwords do not match. Please try again.")
            return

        # Register
        success = user_store.register_user(username, email, password)
        if not success:
            QMessageBox.warning(self, "Email Already Registered",
                                "This email address is already registered.\nPlease log in instead.")
            return

        # Success popup
        msg = QMessageBox(self)
        msg.setWindowTitle("Account Created")
        msg.setText(f"Account created successfully!\nWelcome to OnTrack, {username}!")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

        self.clear_fields()
        self.go_to_login.emit()
