from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor

import user_store
from styles import MAIN_STYLE

TOPBAR_COLOR = "#3b82f6"
DARK_COLOR   = "#1e293b"
BG_COLOR     = "#EEF2F5"
WHITE        = "#FFFFFF"


def make_circle_pixmap(pixmap: QPixmap, size: int) -> QPixmap:
    """Crop pixmap to circle."""
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


class AvatarWidget(QLabel):
    """show avatar icon — if there are no picture use, use default SVG icon"""

    def __init__(self, size: int = 80, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self.set_pixmap(None)

    def set_pixmap(self, pixmap: QPixmap | None):
        if pixmap and not pixmap.isNull():
            self.setPixmap(make_circle_pixmap(pixmap, self._size))
        else:
            self._draw_default()

    def _draw_default(self):
        """draw avatar blue human"""
        result = QPixmap(self._size, self._size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)

        # set profile background blue
        painter.setBrush(QColor("#3b82f6"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self._size, self._size)

        # draw human icon (simplified)
        painter.setBrush(QColor("#FFFFFF"))
        s = self._size
        # head
        head_r = s * 0.18
        head_cx = s * 0.5
        head_cy = s * 0.33
        painter.drawEllipse(
            int(head_cx - head_r), int(head_cy - head_r),
            int(head_r * 2), int(head_r * 2)
        )
        # body (arc / ellipse)
        body_w = s * 0.52
        body_h = s * 0.30
        body_x = s * 0.5 - body_w / 2
        body_y = s * 0.55
        painter.drawEllipse(int(body_x), int(body_y), int(body_w), int(body_h))

        painter.end()
        self.setPixmap(result)


class ProfilePage(QWidget):
    go_to_task        = Signal()
    go_to_edit_profile = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLE)
        self._username = ""
        self._email    = ""
        self._password = ""
        self._avatar_pixmap: QPixmap | None = None
        self._build_ui()

    # ── public ────────────────────────────────────────────────
    def set_user(self, username: str, email: str):
        self._username = username
        self._email    = email
        # get password from store
        pwd = user_store._users.get(email.lower().strip(), {}).get("password", "")
        self._password = pwd
        self._refresh_display()

    def set_avatar(self, pixmap: QPixmap | None):
        self._avatar_pixmap = pixmap
        self.avatar_widget.set_pixmap(pixmap)

    def get_avatar(self) -> QPixmap | None:
        return self._avatar_pixmap

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setFixedWidth(420)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {WHITE};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 36, 32, 32)
        layout.setSpacing(0)

        # Title
        title = QLabel("My Profile")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size:20px; font-weight:700; color:{DARK_COLOR};"
            "font-family:'Segoe UI',Arial,sans-serif; background:transparent;"
        )
        layout.addWidget(title)

        layout.addSpacing(20)

        # Avatar
        avatar_row = QHBoxLayout()
        avatar_row.setAlignment(Qt.AlignCenter)
        self.avatar_widget = AvatarWidget(size=80)
        avatar_row.addWidget(self.avatar_widget)
        layout.addLayout(avatar_row)

        layout.addSpacing(24)

        # Username field (read-only)
        un_lbl = QLabel("Username")
        un_lbl.setStyleSheet(self._field_label_style())
        layout.addWidget(un_lbl)
        layout.addSpacing(6)

        self.username_display = QLabel()
        self.username_display.setStyleSheet(self._field_box_style())
        self.username_display.setMinimumHeight(46)
        layout.addWidget(self.username_display)

        layout.addSpacing(16)

        # Email
        em_lbl = QLabel("Email")
        em_lbl.setStyleSheet(self._field_label_style())
        layout.addWidget(em_lbl)
        layout.addSpacing(6)

        self.email_display = QLabel()
        self.email_display.setStyleSheet(self._field_box_style())
        self.email_display.setMinimumHeight(46)
        layout.addWidget(self.email_display)

        layout.addSpacing(16)

        # Password (masked)
        pw_lbl = QLabel("Password")
        pw_lbl.setStyleSheet(self._field_label_style())
        layout.addWidget(pw_lbl)
        layout.addSpacing(6)

        self.password_display = QLabel()
        self.password_display.setStyleSheet(self._field_box_style())
        self.password_display.setMinimumHeight(46)
        layout.addWidget(self.password_display)

        layout.addSpacing(36)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        back_btn = QPushButton("Back")
        back_btn.setFixedHeight(48)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #EEF2F5; color: {DARK_COLOR};
                border: 1.5px solid #D0D7E2; border-radius: 10px;
                font-size: 14px; font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{ background-color: #D0D7E2; }}
        """)
        back_btn.clicked.connect(self.go_to_task.emit)

        edit_btn = QPushButton("Edit Profile")
        edit_btn.setFixedHeight(48)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_COLOR}; color: white;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{ background-color: #2d3f57; }}
            QPushButton:pressed {{ background-color: #0f1a2e; }}
        """)
        edit_btn.clicked.connect(self.go_to_edit_profile.emit)

        btn_row.addWidget(back_btn)
        btn_row.addWidget(edit_btn)
        layout.addLayout(btn_row)

        outer.addStretch()
        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(card)
        h.addStretch()
        outer.addLayout(h)
        outer.addStretch()

    # ── helpers ───────────────────────────────────────────────
    def _field_label_style(self):
        return (
            f"font-size:14px; font-weight:600; color:{DARK_COLOR};"
            "font-family:'Segoe UI',Arial,sans-serif; background:transparent;"
        )

    def _field_box_style(self):
        return (
            "background-color: #F5F7FA; border: 1.5px solid #D0D7E2;"
            "border-radius: 10px; padding: 10px 14px;"
            f"font-size:14px; color:{DARK_COLOR};"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )

    def _refresh_display(self):
        self.username_display.setText(self._username)
        self.email_display.setText(self._email)
        dot_count = max(len(self._password), 8)
        self.password_display.setText("•" * dot_count)