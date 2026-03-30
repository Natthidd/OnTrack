import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox,
    QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor

import user_store
from styles import styled_msgbox

DARK_COLOR = "#1e293b"
WHITE      = "#FFFFFF"
BG_COLOR   = "#EEF2F5"

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB
ALLOWED_EXTENSIONS  = (".jpg", ".jpeg", ".png")


def make_circle_pixmap(pixmap: QPixmap, size: int) -> QPixmap:
    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    x = (scaled.width()  - size) // 2
    y = (scaled.height() - size) // 2
    painter.drawPixmap(-x, -y, scaled)
    painter.end()
    return result


class AvatarButton(QLabel):
    """วงกลม avatar ที่กดได้ — แสดง camera overlay"""
    clicked = Signal()

    def __init__(self, size: int = 80, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self._user_pixmap: QPixmap | None = None
        self._draw_default()

    def set_pixmap(self, pixmap: QPixmap | None):
        self._user_pixmap = pixmap
        if pixmap and not pixmap.isNull():
            self.setPixmap(make_circle_pixmap(pixmap, self._size))
        else:
            self._draw_default()

    def get_pixmap(self) -> QPixmap | None:
        return self._user_pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def _draw_default(self):
        result = QPixmap(self._size, self._size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#3b82f6"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self._size, self._size)
        painter.setBrush(QColor("#FFFFFF"))
        s = self._size
        head_r = s * 0.18
        painter.drawEllipse(int(s*0.5-head_r), int(s*0.33-head_r),
                             int(head_r*2), int(head_r*2))
        painter.drawEllipse(int(s*0.5-s*0.26), int(s*0.55),
                             int(s*0.52), int(s*0.30))
        painter.end()
        self.setPixmap(result)


class PasswordField(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #F5F7FA;
                border: 1.5px solid #D0D7E2;
                border-radius: 10px;
            }
            QFrame:focus-within { border: 1.5px solid #1e293b; }
        """)
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(4, 0, 4, 0)
        c_layout.setSpacing(0)

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)
        self.input.setStyleSheet("""
            QLineEdit {
                border: none; background: transparent;
                padding: 12px 10px; font-size: 14px; color: #1e293b;
            }
        """)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setObjectName("eyeBtn")
        self.eye_btn.setFixedSize(44, 50)
        self.eye_btn.setCursor(Qt.PointingHandCursor)
        self.eye_btn.setStyleSheet("""
            QPushButton { background:transparent; border:none;
                padding:0px 8px; color:#A0AAB8; }
            QPushButton:hover { color:#1e293b; }
        """)
        self.eye_btn.clicked.connect(self._toggle)
        self._visible = False

        c_layout.addWidget(self.input)
        c_layout.addWidget(self.eye_btn)
        layout.addWidget(container)

    def _toggle(self):
        self._visible = not self._visible
        self.input.setEchoMode(QLineEdit.Normal if self._visible else QLineEdit.Password)
        self.eye_btn.setText("🙈" if self._visible else "👁")

    def text(self):    return self.input.text()
    def clear(self):   self.input.clear()
    def setPlaceholderText(self, t): self.input.setPlaceholderText(t)


class EditProfilePage(QWidget):
    go_to_profile = Signal()          # หลัง Save / Cancel

    # ส่งข้อมูลที่อัพเดตกลับไปที่ MainWindow
    profile_updated = Signal(str, object)   # (new_username, new_avatar_pixmap or None)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._email          = ""
        self._orig_username  = ""
        self._avatar_pixmap: QPixmap | None = None
        self._avatar_path:   str | None     = None
        self._build_ui()

    # ── public ────────────────────────────────────────────────
    def set_user(self, username: str, email: str, avatar: QPixmap | None = None):
        self._orig_username = username
        self._email         = email
        self.username_input.setText(username)
        self.cur_pass_field.clear()
        self.new_pass_field.clear()
        self.confirm_field.clear()

        # โหลด avatar จาก path ที่บันทึกไว้ ถ้ายังไม่มีการส่ง avatar มา
        if avatar is None:
            saved_path = user_store.load_avatar_path(email)
            if saved_path and os.path.exists(saved_path):
                loaded = QPixmap(saved_path)
                if not loaded.isNull():
                    avatar = loaded
                    self._avatar_path = saved_path

        self.avatar_btn.set_pixmap(avatar)
        self._avatar_pixmap = avatar

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setMaximumWidth(420)
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        card.setStyleSheet(f"""
            QWidget {{ background-color: {WHITE}; border-radius: 16px; }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 36, 32, 32)
        layout.setSpacing(0)

        # Title
        title = QLabel("Edit Profile")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size:20px; font-weight:700; color:{DARK_COLOR};"
            "font-family:'Segoe UI',Arial,sans-serif; background:transparent;"
        )
        layout.addWidget(title)

        layout.addSpacing(20)

        # Avatar + camera icon overlay
        avatar_container = QWidget()
        avatar_container.setFixedSize(96, 96)
        avatar_container.setStyleSheet("background:transparent;")
        avatar_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.avatar_btn = AvatarButton(size=80, parent=avatar_container)
        self.avatar_btn.move(8, 8)
        self.avatar_btn.clicked.connect(self._pick_image)

        # Camera overlay badge
        cam_badge = QPushButton("📷", avatar_container)
        cam_badge.setFixedSize(28, 28)
        cam_badge.move(60, 60)
        cam_badge.setCursor(Qt.PointingHandCursor)
        cam_badge.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; border: 2px solid #D0D7E2;
                border-radius: 14px; font-size: 13px; padding: 0;
            }
            QPushButton:hover { background-color: #EEF2F5; }
        """)
        cam_badge.clicked.connect(self._pick_image)

        avatar_row = QHBoxLayout()
        avatar_row.setAlignment(Qt.AlignCenter)
        avatar_row.addWidget(avatar_container)
        layout.addLayout(avatar_row)

        layout.addSpacing(24)

        # Username
        un_lbl = QLabel("Username")
        un_lbl.setStyleSheet(self._lbl_style())
        layout.addWidget(un_lbl)
        layout.addSpacing(6)

        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(46)
        self.username_input.setStyleSheet(self._input_style())
        layout.addWidget(self.username_input)

        layout.addSpacing(16)

        # Current Password
        cp_lbl = QLabel("Current Password")
        cp_lbl.setStyleSheet(self._lbl_style())
        layout.addWidget(cp_lbl)
        layout.addSpacing(6)

        self.cur_pass_field = PasswordField()
        self.cur_pass_field.setPlaceholderText("")
        layout.addWidget(self.cur_pass_field)

        layout.addSpacing(16)

        # New Password
        np_lbl = QLabel("New Password")
        np_lbl.setStyleSheet(self._lbl_style())
        layout.addWidget(np_lbl)
        layout.addSpacing(6)

        self.new_pass_field = PasswordField()
        layout.addWidget(self.new_pass_field)

        layout.addSpacing(4)

        hint = QLabel("Use 8 or more characters with a mix of letters, number & symbols.")
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "font-size:12px; color:#A0AAB8; background:transparent;"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )
        layout.addWidget(hint)

        layout.addSpacing(16)

        # Confirm New Password
        cfm_lbl = QLabel("Confirm New Password")
        cfm_lbl.setStyleSheet(self._lbl_style())
        layout.addWidget(cfm_lbl)
        layout.addSpacing(6)

        self.confirm_field = PasswordField()
        layout.addWidget(self.confirm_field)

        layout.addSpacing(32)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(48)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #EEF2F5; color: {DARK_COLOR};
                border: 1.5px solid #D0D7E2; border-radius: 10px;
                font-size: 14px; font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{ background-color: #D0D7E2; }}
        """)
        cancel_btn.clicked.connect(self._on_cancel)

        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(48)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_COLOR}; color: white;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{ background-color: #2d3f57; }}
            QPushButton:pressed {{ background-color: #0f1a2e; }}
        """)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        outer.addStretch()
        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(card)
        h.addStretch()
        outer.addLayout(h)
        outer.addStretch()

    # ── pick image ────────────────────────────────────────────
    def _pick_image(self):
        styled_msgbox(
            self,
            "Image Requirements",
            "Please select an image file.\n\n"
            "• Allowed formats: JPG, PNG\n"
            "• Maximum file size: 10 MB",
            QMessageBox.Information,
        ).exec()

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "",
            "Images (*.jpg *.jpeg *.png);;All Files (*)"
        )
        if not path:
            return

        # ── Validation ────────────────────────────
        ext = os.path.splitext(path)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            styled_msgbox(
                self, "Invalid File Type",
                f"The selected file type '{ext}' is not supported.\n"
                "Please choose a JPG or PNG image.",
                QMessageBox.Warning,
            ).exec()
            return

        file_size = os.path.getsize(path)
        if file_size > MAX_FILE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            styled_msgbox(
                self, "File Too Large",
                f"The selected file is {size_mb:.1f} MB.\n"
                "Maximum allowed size is 10 MB.\n"
                "Please choose a smaller image.",
                QMessageBox.Warning,
            ).exec()
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            styled_msgbox(
                self, "Cannot Load Image",
                "The selected file could not be loaded as an image.\n"
                "Please try a different file.",
                QMessageBox.Warning,
            ).exec()
            return

        self._avatar_pixmap = pixmap
        self._avatar_path   = path          # จำ path ไว้บันทึก
        self.avatar_btn.set_pixmap(pixmap)

    # ── save ──────────────────────────────────────────────────
    def _on_save(self):
        new_username = self.username_input.text().strip()
        cur_pass     = self.cur_pass_field.text()
        new_pass     = self.new_pass_field.text()
        confirm      = self.confirm_field.text()

        if not new_username:
            styled_msgbox(self, "Missing Fields",
                          "Username cannot be empty.",
                          QMessageBox.Warning).exec()
            return

        # ถ้า user กรอก password field ใดก็ตาม → ต้องเปลี่ยน password ด้วย
        wants_pw_change = bool(cur_pass or new_pass or confirm)

        if wants_pw_change:
            # ตรวจ current password
            stored_pw = user_store._users.get(
                self._email.lower().strip(), {}
            ).get("password", "")
            if cur_pass != stored_pw:
                styled_msgbox(self, "Incorrect Password",
                              "The current password you entered is incorrect.",
                              QMessageBox.Warning).exec()
                return

            if len(new_pass) < 8:
                styled_msgbox(self, "Weak Password",
                              "New password must be at least 8 characters long.",
                              QMessageBox.Warning).exec()
                return

            if new_pass != confirm:
                styled_msgbox(self, "Password Mismatch",
                              "New password and confirmation do not match.",
                              QMessageBox.Warning).exec()
                return

            # บันทึก password ใหม่
            user_store.reset_password(self._email, new_pass)

        # บันทึก username ใหม่
        email_key = self._email.lower().strip()
        if email_key in user_store._users:
            user_store._users[email_key]["username"] = new_username
            user_store._save_users()

        # บันทึก avatar path ถ้ามีการเลือกรูปใหม่
        if self._avatar_path:
            user_store.save_avatar_path(self._email, self._avatar_path)

        # ส่งข้อมูลออกไป
        self.profile_updated.emit(new_username, self._avatar_pixmap)
        self.go_to_profile.emit()

    def _on_cancel(self):
        self.go_to_profile.emit()

    # ── style helpers ─────────────────────────────────────────
    def _lbl_style(self):
        return (
            f"font-size:14px; font-weight:600; color:{DARK_COLOR};"
            "font-family:'Segoe UI',Arial,sans-serif; background:transparent;"
        )

    def _input_style(self):
        return (
            "background-color:#F5F7FA; border:1.5px solid #D0D7E2;"
            "border-radius:10px; padding:10px 14px;"
            f"font-size:14px; color:{DARK_COLOR};"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )