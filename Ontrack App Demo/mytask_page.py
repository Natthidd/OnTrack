from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QFileDialog, QMenuBar, QMenu,
    QDialog, QLineEdit, QDateEdit, QTimeEdit, QTextEdit,
    QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QTimer
from PySide6.QtGui import QAction, QFont, QColor, QPixmap, QPainter, QPainterPath

import user_store
from styles import styled_msgbox

TOPBAR_COLOR = "#3b82f6"
TITLE_COLOR  = "#1e293b"
BG_COLOR     = "#EEF2F5"
DARK_COLOR   = "#1e293b"
WHITE        = "#FFFFFF"
DONE_ROW_BG  = "#d1fae5"
DONE_ROW_FG  = "#10b981"

CATEGORIES = ["Homework", "Exam", "Reading", "Exercise", "Other"]

STATUS_COLOR = {
    "Overdue":   "#E05252",
    "Success":   "#10b981",
    "Due Today": "#f59e0b",
    "Upcoming":  "#3b82f6",
}


def compute_status(due_dt: datetime, done: bool) -> str:
    if done:
        return "Success"
    now = datetime.now()
    if due_dt.date() == now.date():
        return "Due Today"
    if due_dt < now:
        return "Overdue"
    return "Upcoming"


# ── Avatar helpers ─────────────────────────────────────────────────────────────
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


class TopbarAvatar(QLabel):
    """Avatar วงกลมเล็กๆ ใน topbar — กดได้"""
    clicked = Signal()

    def __init__(self, size: int = 32, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("View Profile")
        self._draw_default()

    def set_pixmap(self, pixmap: QPixmap | None):
        if pixmap and not pixmap.isNull():
            self.setPixmap(make_circle_pixmap(pixmap, self._size))
        else:
            self._draw_default()

    def _draw_default(self):
        result = QPixmap(self._size, self._size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self._size, self._size)
        # วาด icon คนสีน้ำเงิน
        painter.setBrush(QColor(TOPBAR_COLOR))
        s = self._size
        head_r = s * 0.18
        painter.drawEllipse(int(s*0.5-head_r), int(s*0.28-head_r),
                             int(head_r*2), int(head_r*2))
        painter.drawEllipse(int(s*0.5-s*0.26), int(s*0.50),
                             int(s*0.52), int(s*0.30))
        painter.end()
        self.setPixmap(result)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


# ── Add / Edit Dialog ──────────────────────────────────────────────────────────
class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Task")
        self.setFixedWidth(400)
        self.setModal(True)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {WHITE};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                font-size: 13px; color: {DARK_COLOR};
                font-weight: 600; background: transparent;
            }}
            QLineEdit, QDateEdit, QTimeEdit, QTextEdit {{
                background-color: #F5F7FA;
                border: 1.5px solid #D0D7E2;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 13px; color: {DARK_COLOR};
            }}
            QLineEdit:focus, QDateEdit:focus,
            QTimeEdit:focus, QTextEdit:focus {{
                border: 1.5px solid {TOPBAR_COLOR};
            }}
        """)
        self._selected_category = CATEGORIES[0]
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self._head_label = QLabel("Create New Task")
        self._head_label.setStyleSheet(f"font-size:16px; font-weight:700; color:{DARK_COLOR};")
        layout.addWidget(self._head_label)

        layout.addWidget(QLabel("Task Name"))
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(38)
        self.name_input.setPlaceholderText("Enter task name…")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Select Category"))
        cat_row = QHBoxLayout()
        cat_row.setSpacing(4)
        self._cat_buttons: dict[str, QPushButton] = {}
        for cat in CATEGORIES:
            btn = QPushButton(cat)
            btn.setCheckable(False)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, c=cat: self._select_category(c))
            self._cat_buttons[cat] = btn
            cat_row.addWidget(btn)
        layout.addLayout(cat_row)
        self._select_category(CATEGORIES[0])

        layout.addWidget(QLabel("Date"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumHeight(38)
        self.date_input.setDisplayFormat("dd MMM yyyy")
        layout.addWidget(self.date_input)

        layout.addWidget(QLabel("Time"))
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setMinimumHeight(38)
        self.time_input.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_input)

        layout.addWidget(QLabel("Description"))
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(70)
        self.desc_input.setPlaceholderText("Optional description…")
        layout.addWidget(self.desc_input)

        layout.addSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(42)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #EEF2F5; color: {DARK_COLOR};
                border: 1.5px solid #D0D7E2; border-radius: 10px;
                font-size: 14px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #D0D7E2; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        self.add_btn = QPushButton("+Add Task")
        self.add_btn.setFixedHeight(42)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_COLOR}; color: white;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #2d3f57; }}
        """)
        self.add_btn.clicked.connect(self._on_add)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.add_btn)
        layout.addLayout(btn_row)

    def _select_category(self, cat: str):
        self._selected_category = cat
        for c, btn in self._cat_buttons.items():
            if c == cat:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {TOPBAR_COLOR}; color: white;
                        border: none; border-radius: 8px;
                        font-size: 11px; font-weight: 700; padding: 4px 6px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #EEF2F5; color: {DARK_COLOR};
                        border: 1.5px solid #D0D7E2; border-radius: 8px;
                        font-size: 11px; font-weight: 600; padding: 4px 6px;
                    }}
                    QPushButton:hover {{ background-color: #dbeafe; }}
                """)

    def _on_add(self):
        if not self.name_input.text().strip():
            styled_msgbox(self, "Missing Fields",
                          "Please enter a task name.",
                          QMessageBox.Warning).exec()
            return
        self.accept()

    def get_task(self) -> dict:
        d = self.date_input.date()
        t = self.time_input.time()
        due_dt = datetime(d.year(), d.month(), d.day(), t.hour(), t.minute())
        return {
            "name":     self.name_input.text().strip(),
            "category": self._selected_category,
            "due_dt":   due_dt,
            "desc":     self.desc_input.toPlainText().strip(),
            "done":     False,
        }

    def prefill(self, task: dict):
        self.setWindowTitle("Edit Task")
        self._head_label.setText("Edit Task")
        self.add_btn.setText("Update Task")
        self.name_input.setText(task["name"])
        self._select_category(task.get("category", CATEGORIES[0]))
        dt = task["due_dt"]
        self.date_input.setDate(QDate(dt.year, dt.month, dt.day))
        self.time_input.setTime(QTime(dt.hour, dt.minute))
        self.desc_input.setPlainText(task.get("desc", ""))


# ── Draggable Table ────────────────────────────────────────────────────────────
# ── Draggable Table ────────────────────────────────────────────────────────────
class DraggableTable(QTableWidget):
    """Drag-to-reorder ใช้ mouse events — highlight แถวด้วย selectRow (สีฟ้า)
    ไม่มีกรอบ dotted ของ OS"""
    row_moved = Signal(int, int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drag_src: int = -1
        self._drag_active: bool = False
        self._drag_start_y: int = 0
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDragDropMode(QTableWidget.NoDragDrop)
        self.setDropIndicatorShown(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            row = self.rowAt(event.position().toPoint().y())
            if row >= 0:
                self._drag_src     = row
                self._drag_start_y = event.position().toPoint().y()
                self._drag_active  = False
                self.selectRow(row)   # highlight ทันทีที่คลิก
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_src >= 0 and (event.buttons() & Qt.LeftButton):
            dy = abs(event.position().toPoint().y() - self._drag_start_y)
            if dy > 6:
                self._drag_active = True
                # highlight แถวที่เมาส์อยู่ตอนลาก
                hover_row = self.rowAt(event.position().toPoint().y())
                if hover_row >= 0:
                    self.selectRow(hover_row)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drag_active:
            dst = self.rowAt(event.position().toPoint().y())
            if dst < 0:
                dst = self.rowCount() - 1
            if dst != self._drag_src and self._drag_src >= 0 and dst >= 0:
                self.row_moved.emit(self._drag_src, dst)
            QTimer.singleShot(0, self.clearSelection)
        elif event.button() == Qt.LeftButton:
            # คลิกธรรมดา — ล้าง selection หลัง 200ms
            QTimer.singleShot(200, self.clearSelection)
        self._drag_src    = -1
        self._drag_active = False
        super().mouseReleaseEvent(event)


# ── Task Page ──────────────────────────────────────────────────────────────────
class TaskPage(QWidget):
    go_to_login   = Signal()
    go_to_profile = Signal()
    go_to_graph   = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = ""
        self._email   = ""
        self._tasks: list[dict] = []
        self._rebuilding = False
        self._build_ui()

    def set_user(self, username: str, email: str):
        self.username = username
        self._email   = email
        self.user_label.setText(username)
        self._tasks = user_store.load_tasks(email)
        self._refresh_table()

    def set_username(self, username: str):
        self.username = username
        self.user_label.setText(username)

    def set_avatar(self, pixmap: QPixmap | None):
        """อัพเดต avatar ใน topbar"""
        self.topbar_avatar.set_pixmap(pixmap)

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #ccc;")
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(4, 0, 8, 0)
        tb_layout.setSpacing(0)

        menu_bar = QMenuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: transparent; color: #1e293b;
                font-size: 13px; font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMenuBar::item { background: transparent; padding: 4px 10px; }
            QMenuBar::item:selected { background-color: #d0d7e2; border-radius: 4px; }
            QMenu {
                background-color: #ffffff; border: 1px solid #D0D7E2;
                font-size: 13px; color: #1e293b;
            }
            QMenu::item { padding: 7px 24px; }
            QMenu::item:selected { background-color: #EEF2F5; }
        """)
        save_menu = QMenu("💾  Save File", menu_bar)
        act_table = QAction("📥  Save Table", self)
        act_table.triggered.connect(self._save_table)
        act_graph = QAction("📊  Save Graph", self)
        act_graph.triggered.connect(self._save_graph)
        save_menu.addAction(act_table)
        save_menu.addAction(act_graph)
        menu_bar.addMenu(save_menu)
        tb_layout.addWidget(menu_bar)
        tb_layout.addStretch()
        root.addWidget(title_bar)

        # top bar
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_bar.setStyleSheet(f"background-color: {TOPBAR_COLOR};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 0, 0, 0)
        top_layout.setSpacing(0)

        app_title = QLabel("OnTrack")
        app_title.setStyleSheet(
            f"font-size:24px; font-weight:800; color:{TITLE_COLOR};"
            f"background-color:{TOPBAR_COLOR}; font-family:'Segoe UI',Arial,sans-serif;"
        )
        top_layout.addWidget(app_title)
        top_layout.addStretch()

        # ── Avatar (แทน 👤 emoji) ──────────────────────────────
        self.topbar_avatar = TopbarAvatar(size=34)
        self.topbar_avatar.clicked.connect(self.go_to_profile.emit)
        top_layout.addWidget(self.topbar_avatar)
        top_layout.addSpacing(8)

        self.user_label = QLabel(self.username)
        self.user_label.setStyleSheet(
            f"font-size:13px; color:{WHITE}; background:{TOPBAR_COLOR};"
            f"font-family:'Segoe UI',Arial,sans-serif; margin-left:6px;"
        )
        top_layout.addWidget(self.user_label)
        top_layout.addSpacing(8)

        logout_btn = QPushButton("➜]")
        logout_btn.setToolTip("Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setFixedSize(44, 60)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color:{TOPBAR_COLOR}; border:none;
                color:{WHITE}; font-size:18px;
            }}
            QPushButton:hover {{ background-color:#2563eb; }}
        """)
        logout_btn.clicked.connect(self._do_logout)

        top_layout.addWidget(logout_btn)
        root.addWidget(top_bar)

        # content
        content = QWidget()
        content.setStyleSheet(f"background-color:{BG_COLOR};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(14)

        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        sec_title = QLabel("My Task")
        sec_title.setStyleSheet(
            f"font-size:20px; font-weight:700; color:{DARK_COLOR};"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )
        sec_sub = QLabel("Ready to crush your goals?")
        sec_sub.setStyleSheet(
            "font-size:13px; color:#5A6478; font-family:'Segoe UI',Arial,sans-serif;"
        )
        title_col.addWidget(sec_title)
        title_col.addWidget(sec_sub)
        header_row.addLayout(title_col)
        header_row.addStretch()

        btn_col = QVBoxLayout()
        btn_col.setSpacing(4)
        btn_col.setAlignment(Qt.AlignRight)
        btn_row_w = QHBoxLayout()
        btn_row_w.setSpacing(8)
        btn_row_w.setAlignment(Qt.AlignRight)

        add_btn = QPushButton()
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedSize(50, 50)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color:{TOPBAR_COLOR};
                border:none; border-radius:10px;
            }}
            QPushButton:hover {{ background-color:#2563eb; }}
        """)
        _plus = QLabel("+", add_btn)
        _plus.setAlignment(Qt.AlignCenter)
        _plus.setGeometry(0, 0, 50, 50)
        _plus.setStyleSheet(
            "color:white; font-size:28px; font-weight:900;"
            "background:transparent; border:none; padding-bottom:2px;"
        )
        _plus.setAttribute(Qt.WA_TransparentForMouseEvents)
        add_btn.clicked.connect(self._open_add_dialog)

        graph_btn = QPushButton("📊")
        graph_btn.setCursor(Qt.PointingHandCursor)
        graph_btn.setFixedSize(50, 50)
        graph_btn.setFont(QFont("Segoe UI", 18))
        graph_btn.setStyleSheet(f"""
            QPushButton {{
                background-color:{TOPBAR_COLOR}; color:white;
                border:none; border-radius:10px; padding:0px; text-align:center;
            }}
            QPushButton:hover {{ background-color:#2563eb; }}
        """)

        graph_btn.clicked.connect(self.go_to_graph.emit)

        btn_row_w.addWidget(add_btn)
        btn_row_w.addWidget(graph_btn)

        add_label = QLabel("+Add Task")
        add_label.setAlignment(Qt.AlignCenter)
        add_label.setStyleSheet(
            "font-size:11px; color:#5A6478; font-family:'Segoe UI',Arial,sans-serif;"
        )
        btn_col.addLayout(btn_row_w)
        btn_col.addWidget(add_label)
        header_row.addLayout(btn_col)
        cl.addLayout(header_row)

        # table
        self.table = DraggableTable()
        self.table.row_moved.connect(self._on_row_moved)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["", "Status", "Task Name", "Due Date", ""])
        self.table.setRowCount(8)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setSectionsMovable(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {WHITE};
                border: 1.5px solid #D0D7E2;
                border-radius: 10px;
                gridline-color: #E4EAF2;
                font-size: 13px; color: {DARK_COLOR};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QTableWidget::item {{ padding: 6px 8px; border: none; outline: none; }}
            QTableWidget::item:hover {{ border: none; outline: none; background-color: #eff6ff; }}
            QTableWidget::item:selected {{ background-color: #bfdbfe; color: {DARK_COLOR}; border: none; outline: none; }}
            QTableWidget::item:selected:hover {{ background-color: #bfdbfe; border: none; outline: none; }}
            QTableWidget::item:focus {{ border: none; outline: none; }}
            QTableWidget::drop-indicator {{ background: transparent; border: none; image: none; width: 0; height: 0; }}
            QHeaderView::section {{
                background-color: {TOPBAR_COLOR};
                color: white; font-size: 13px; font-weight: 600;
                padding: 10px 8px; border: none;
            }}
            QHeaderView::section:first {{ border-top-left-radius: 8px; }}
            QHeaderView::section:last  {{ border-top-right-radius: 8px; }}
        """)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed);  self.table.setColumnWidth(0, 48)
        hh.setSectionResizeMode(1, QHeaderView.Fixed);  self.table.setColumnWidth(1, 90)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.Fixed);  self.table.setColumnWidth(3, 150)
        hh.setSectionResizeMode(4, QHeaderView.Fixed);  self.table.setColumnWidth(4, 76)

        for r in range(8):
            self.table.setRowHeight(r, 44)

        cl.addWidget(self.table)
        root.addWidget(content)

    # ── dialogs & table logic (unchanged) ─────────────────────
    def _open_add_dialog(self):
        dlg = AddTaskDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._tasks.insert(0, dlg.get_task())   # ← insert at top
            self._persist()
            self._refresh_table()

    def _refresh_table(self):
        if self._rebuilding:
            return
        self._rebuilding = True

        n    = len(self._tasks)
        rows = max(n + 3, 8)
        self.table.setRowCount(rows)

        for r in range(rows):
            self.table.setRowHeight(r, 44)

        for r, task in enumerate(self._tasks):
            done   = task["done"]
            status = compute_status(task["due_dt"], done)
            task["status"] = status

            row_bg = QColor(DONE_ROW_BG) if done else QColor(WHITE)
            row_fg = QColor(DONE_ROW_FG) if done else QColor(DARK_COLOR)

            task_index = r
            chk = QPushButton("✓" if done else "")
            chk.setFixedSize(20, 20)
            chk.setCursor(Qt.PointingHandCursor)
            chk.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#10b981' if done else '#ffffff'};
                    color: white;
                    border: 2px solid {'#10b981' if done else '#9ca3af'};
                    border-radius: 4px;
                    font-size: 12px; font-weight: bold;
                    padding: 0px; margin: 0px;
                }}
                QPushButton:hover {{
                    border: 2px solid {'#059669' if done else '#3b82f6'};
                    background-color: {'#059669' if done else '#eff6ff'};
                }}
            """)
            chk.clicked.connect(
                lambda _, idx=task_index: self._on_checkbox(idx, not self._tasks[idx]["done"])
            )

            cell0 = QWidget()
            cell0.setStyleSheet(f"background-color: {DONE_ROW_BG if done else WHITE};")
            h0 = QHBoxLayout(cell0)
            h0.addWidget(chk)
            h0.setAlignment(Qt.AlignCenter)
            h0.setContentsMargins(4, 4, 4, 4)
            h0.setSpacing(0)
            self.table.setCellWidget(r, 0, cell0)

            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor(STATUS_COLOR.get(status, DARK_COLOR)))
            status_item.setBackground(row_bg)
            self.table.setItem(r, 1, status_item)

            name_item = QTableWidgetItem(task["name"])
            if done:
                f = name_item.font()
                f.setStrikeOut(True)
                name_item.setFont(f)
            name_item.setForeground(row_fg)
            name_item.setBackground(row_bg)
            self.table.setItem(r, 2, name_item)

            due_str = task["due_dt"].strftime("%d %b, %Y %H:%M")
            date_item = QTableWidgetItem(due_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setForeground(row_fg)
            date_item.setBackground(row_bg)
            self.table.setItem(r, 3, date_item)

            action_w = QWidget()
            action_w.setStyleSheet(f"background-color: {DONE_ROW_BG if done else WHITE};")
            ah = QHBoxLayout(action_w)
            ah.setContentsMargins(4, 0, 4, 0)
            ah.setSpacing(4)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(26, 26)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton { background:transparent; border:none;
                    font-size:14px; color:#5A6478; }
                QPushButton:hover { color:#3b82f6; }
            """)
            edit_btn.clicked.connect(lambda _, i=r: self._edit_task(i))

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(26, 26)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton { background:transparent; border:none;
                    font-size:14px; color:#5A6478; }
                QPushButton:hover { color:#E05252; }
            """)
            del_btn.clicked.connect(lambda _, i=r: self._delete_task(i))

            ah.addWidget(edit_btn)
            ah.addWidget(del_btn)
            self.table.setCellWidget(r, 4, action_w)

        for r in range(n, rows):
            for c in range(5):
                self.table.removeCellWidget(r, c)
                self.table.setItem(r, c, QTableWidgetItem(""))

        self._rebuilding = False

    def _on_checkbox(self, index: int, checked: bool):
        if index >= len(self._tasks):
            return
        self._tasks[index]["done"] = checked
        task = self._tasks.pop(index)
        if checked:
            self._tasks.append(task)
        else:
            self._tasks.insert(0, task)
        self._persist()
        QTimer.singleShot(0, self._refresh_table)

    def _edit_task(self, index: int):
        if index >= len(self._tasks):
            return
        dlg = AddTaskDialog(self)
        dlg.prefill(self._tasks[index])
        if dlg.exec() == QDialog.Accepted:
            new_task = dlg.get_task()
            new_task["done"] = self._tasks[index]["done"]
            self._tasks[index] = new_task
            self._persist()
            self._refresh_table()

    def _delete_task(self, index: int):
        if index >= len(self._tasks):
            return
        msg = styled_msgbox(
            self, "Delete Task",
            f"Are you sure you want to delete\n\"{self._tasks[index]['name']}\"?",
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No,
        )
        if msg.exec() == QMessageBox.Yes:
            self._tasks.pop(index)
            self._persist()
            self._refresh_table()

    def _persist(self):
        if self._email:
            user_store.save_tasks(self._email, self._tasks)

    def _save_table(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Table", "my_tasks", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Status,Task Name,Due Date,Category,Done\n")
                for task in self._tasks:
                    status  = compute_status(task["due_dt"], task["done"])
                    due_str = task["due_dt"].strftime("%d %b %Y %H:%M")
                    f.write(
                        f"{status},{task['name']},{due_str},"
                        f"{task.get('category','')},{task['done']}\n"
                    )
        except Exception as e:
            styled_msgbox(self, "Save Error", str(e), QMessageBox.Warning).exec()

    def _save_graph(self):
        styled_msgbox(self, "Save Graph",
                      "Graph export is not available yet.",
                      QMessageBox.Information).exec()

    def _do_logout(self):
        self.go_to_login.emit()

    def _on_row_moved(self, src: int, dst: int):
        if src >= len(self._tasks) or dst >= len(self._tasks):
            QTimer.singleShot(0, self._refresh_table)
            return
        task = self._tasks.pop(src)
        self._tasks.insert(dst, task)
        self._persist()
        QTimer.singleShot(0, self._refresh_table)