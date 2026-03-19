from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

import user_store
from styles import MAIN_STYLE, styled_msgbox


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
                border: 1.5px solid #1e293b;
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
                color: #1e293b;
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


class ResetPasswordPage(QWidget):
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
        title = QLabel("OnTrack")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(6)

        subtitle = QLabel("Reset your password below.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(32)

        section = QLabel("Forgot Password?")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        layout.addSpacing(8)

        desc = QLabel("Enter the email address linked to your account,\nthen choose a new password.")
        desc.setObjectName("linkText")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(24)

        # Email
        email_lbl = QLabel("Email Address")
        email_lbl.setObjectName("fieldLabel")
        layout.addWidget(email_lbl)
        layout.addSpacing(6)

        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(50)
        layout.addWidget(self.email_input)

        layout.addSpacing(16)

        # New Password
        pw_lbl = QLabel("New Password")
        pw_lbl.setObjectName("fieldLabel")
        layout.addWidget(pw_lbl)
        layout.addSpacing(6)

        self.pass_field = PasswordField()
        layout.addWidget(self.pass_field)

        layout.addSpacing(6)

        hint = QLabel("Use 8 or more characters with a mix of letters, numbers & symbols.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addSpacing(16)

        # Confirm Password
        cp_lbl = QLabel("Confirm New Password")
        cp_lbl.setObjectName("fieldLabel")
        layout.addWidget(cp_lbl)
        layout.addSpacing(6)

        self.confirm_field = PasswordField()
        layout.addWidget(self.confirm_field)

        layout.addSpacing(32)

        # Reset button
        reset_btn = QPushButton("Reset Password")
        reset_btn.setObjectName("mainBtn")
        reset_btn.setMinimumHeight(56)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self._do_reset)
        layout.addWidget(reset_btn)

        layout.addSpacing(20)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #D0D7E2; max-height: 1px;")
        layout.addWidget(divider)

        layout.addSpacing(16)

        # Back to login row
        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignCenter)
        back_lbl = QLabel("Remembered your password?")
        back_lbl.setObjectName("linkText")
        back_btn = QPushButton("Login")
        back_btn.setObjectName("linkBtn")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self._go_back)
        bottom_row.addWidget(back_lbl)
        bottom_row.addSpacing(4)
        bottom_row.addWidget(back_btn)
        layout.addLayout(bottom_row)

        # Center card
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
        self.confirm_field.clear()

    def _do_reset(self):
        email = self.email_input.text().strip()
        password = self.pass_field.text()
        confirm = self.confirm_field.text()

        # --- Validation ---
        if not email or not password or not confirm:
            styled_msgbox(self, "Missing Fields",
                          "Please fill in all fields.",
                          QMessageBox.Warning).exec()
            return

        if not user_store.email_exists(email):
            styled_msgbox(self, "Email Not Found",
                          "No account found with that email address.\nPlease check and try again.",
                          QMessageBox.Warning).exec()
            return

        if len(password) < 8:
            styled_msgbox(self, "Weak Password",
                          "Password must be at least 8 characters long.",
                          QMessageBox.Warning).exec()
            return

        if password != confirm:
            styled_msgbox(self, "Password Mismatch",
                          "Passwords do not match. Please try again.",
                          QMessageBox.Warning).exec()
            return

        # --- Reset ---
        user_store.reset_password(email, password)

        styled_msgbox(self, "Password Reset",
                      "Your password has been reset successfully!\nYou can now log in with your new password.",
                      QMessageBox.Information).exec()

        self.clear_fields()
        self.go_to_login.emit()

    def _go_back(self):
        self.clear_fields()
        self.go_to_login.emit()