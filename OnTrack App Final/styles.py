BG_COLOR = "#EEF2F5"
DARK_COLOR = "#1e293b"
INPUT_BG = "#FFFFFF"
INPUT_BORDER = "#D0D7E2"
PLACEHOLDER_COLOR = "#A0AAB8"
LABEL_COLOR = "#1e293b"
SUBTITLE_COLOR = "#5A6478"
LINK_COLOR = "#4A90D9"
ERROR_COLOR = "#E05252"

MAIN_STYLE = f"""
    QWidget {{
        background-color: {BG_COLOR};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    QLabel#title {{
        font-size: 32px;
        font-weight: 800;
        color: {DARK_COLOR};
    }}
    QLabel#subtitle {{
        font-size: 15px;
        color: {SUBTITLE_COLOR};
    }}
    QLabel#sectionTitle {{
        font-size: 18px;
        font-weight: 700;
        color: {DARK_COLOR};
    }}
    QLabel#fieldLabel {{
        font-size: 14px;
        color: {LABEL_COLOR};
        font-weight: 400;
    }}
    QLabel#hint {{
        font-size: 12px;
        color: {PLACEHOLDER_COLOR};
    }}
    QLabel#linkText {{
        font-size: 13px;
        color: {SUBTITLE_COLOR};
    }}
    QLineEdit {{
        background-color: {INPUT_BG};
        border: 1.5px solid {INPUT_BORDER};
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 14px;
        color: {DARK_COLOR};
    }}
    QLineEdit:focus {{
        border: 1.5px solid {DARK_COLOR};
    }}
    QPushButton#mainBtn {{
        background-color: {DARK_COLOR};
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        padding: 16px;
    }}
    QPushButton#mainBtn:hover {{
        background-color: #2d3f57;
    }}
    QPushButton#mainBtn:pressed {{
        background-color: #0f1a2e;
    }}
    QPushButton#linkBtn {{
        background: transparent;
        border: none;
        color: {LINK_COLOR};
        font-size: 13px;
        font-weight: 500;
        text-decoration: underline;
        padding: 0;
    }}
    QPushButton#linkBtn:hover {{
        color: #2A6DB5;
    }}
    QPushButton#eyeBtn {{
        background: transparent;
        border: none;
        padding: 0px 8px;
        color: {PLACEHOLDER_COLOR};
    }}
    QPushButton#eyeBtn:hover {{
        color: {DARK_COLOR};
    }}
    QFrame#divider {{
        color: {INPUT_BORDER};
    }}
"""

# --- Force light theme on all QMessageBox pop-ups ---
MSGBOX_STYLE = f"""
    QMessageBox {{
        background-color: {BG_COLOR};
        color: {DARK_COLOR};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }}
    QMessageBox QLabel {{
        color: {DARK_COLOR};
        background-color: transparent;
        font-size: 13px;
    }}
    QMessageBox QPushButton {{
        background-color: {DARK_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: 600;
        min-width: 80px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: #2d3f57;
    }}
    QMessageBox QPushButton:pressed {{
        background-color: #0f1a2e;
    }}
"""


def styled_msgbox(parent, title: str, text: str, icon, buttons=None):
    """
    Drop-in helper that creates a QMessageBox with a forced light stylesheet
    so it looks correct on both light and dark OS themes.

    Usage:
        from styles import styled_msgbox
        from PySide6.QtWidgets import QMessageBox

        styled_msgbox(self, "Title", "Message", QMessageBox.Warning)
    """
    from PySide6.QtWidgets import QMessageBox as _QMB
    msg = _QMB(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    msg.setStyleSheet(MSGBOX_STYLE)
    if buttons is not None:
        msg.setStandardButtons(buttons)
    return msg













