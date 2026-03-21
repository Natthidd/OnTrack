from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QFileDialog, QMenuBar, QMenu,
    QDialog, QLineEdit, QDateEdit, QTimeEdit, QTextEdit,
    QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QTimer, QTimer
from PySide6.QtGui import QAction, QFont, QColor

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


# ── Add / Edit Dialog ──────────────────────────────────────────────────────────
class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Task")
        self.setFixedWidth(340)
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

        head = QLabel("Create New Task")
        head.setStyleSheet(f"font-size:16px; font-weight:700; color:{DARK_COLOR};")
        layout.addWidget(head)

        layout.addWidget(QLabel("Task Name"))
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(38)
        self.name_input.setPlaceholderText("Enter task name…")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Select Category"))
        cat_row = QHBoxLayout()
        cat_row.setSpacing(6)
        self._cat_buttons: dict[str, QPushButton] = {}
        for cat in CATEGORIES:
            btn = QPushButton(cat)
            btn.setCheckable(False)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
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

        add_btn = QPushButton("+ Add Task")
        add_btn.setFixedHeight(42)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_COLOR}; color: white;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #2d3f57; }}
        """)
        add_btn.clicked.connect(self._on_add)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

    def _select_category(self, cat: str):
        self._selected_category = cat
        for c, btn in self._cat_buttons.items():
            if c == cat:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {TOPBAR_COLOR}; color: white;
                        border: none; border-radius: 8px;
                        font-size: 12px; font-weight: 600; padding: 4px 8px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #EEF2F5; color: {DARK_COLOR};
                        border: 1.5px solid #D0D7E2; border-radius: 8px;
                        font-size: 12px; padding: 4px 8px;
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
        self.name_input.setText(task["name"])
        self._select_category(task.get("category", CATEGORIES[0]))
        dt = task["due_dt"]
        self.date_input.setDate(QDate(dt.year, dt.month, dt.day))
        self.time_input.setTime(QTime(dt.hour, dt.minute))
        self.desc_input.setPlainText(task.get("desc", ""))


# ── Draggable Table ────────────────────────────────────────────────────────────
class DraggableTable(QTableWidget):
    """QTableWidget ที่ override dropEvent เพื่อ sync _tasks หลัง drag&drop"""
    row_moved = Signal(int, int)   # (from_row, to_row)

    def dropEvent(self, event):
        src_row = self.currentRow()
        # คำนวณ dst จาก drop position ก่อน super() ขยับ row
        dst_row = self.indexAt(event.position().toPoint()).row()
        if dst_row < 0:
            dst_row = self.rowCount() - 1
        # บล็อก super() ไม่ให้ขยับ row เอง (เราจะ _refresh_table เอง)
        event.setDropAction(Qt.IgnoreAction)
        event.accept()
        if src_row != dst_row and src_row >= 0 and dst_row >= 0:
            self.row_moved.emit(src_row, dst_row)


# ── Task Page ──────────────────────────────────────────────────────────────────
class TaskPage(QWidget):
    go_to_login = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = ""
        self._email   = ""
        self._tasks: list[dict] = []
        self._rebuilding = False          # guard flag
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

        user_icon = QLabel("👤")
        user_icon.setStyleSheet(f"color:{WHITE}; font-size:15px; background:{TOPBAR_COLOR};")

        self.user_label = QLabel(self.username)
        self.user_label.setStyleSheet(
            f"font-size:13px; color:{WHITE}; background:{TOPBAR_COLOR};"
            f"font-family:'Segoe UI',Arial,sans-serif; margin-left:6px;"
        )

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

        top_layout.addWidget(user_icon)
        top_layout.addWidget(self.user_label)
        top_layout.addSpacing(8)
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
            f"font-family:'Segoe UI',Arial,sans-serif;"
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

        btn_row_w.addWidget(add_btn)
        btn_row_w.addWidget(graph_btn)
        add_label = QLabel("Add Task here!")
        add_label.setAlignment(Qt.AlignCenter)
        add_label.setStyleSheet(
            "font-size:11px; color:#5A6478; font-family:'Segoe UI',Arial,sans-serif;"
        )
        btn_col.addLayout(btn_row_w)
        btn_col.addWidget(add_label)
        header_row.addLayout(btn_col)
        cl.addLayout(header_row)

        # table — 5 cols: ☑ | Status | Task Name | Due Date | Actions
        self.table = DraggableTable()
        self.table.row_moved.connect(self._on_row_moved)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["", "Status", "Task Name", "Due Date", ""])
        self.table.setRowCount(8)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setDragDropMode(QTableWidget.InternalMove)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setSectionsMovable(True)
        self.table.setFocusPolicy(Qt.StrongFocus)
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
            QTableWidget::item {{ padding: 6px 8px; border: none; }}
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

    # ── open add dialog ───────────────────────────────────────
    def _open_add_dialog(self):
        dlg = AddTaskDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._tasks.append(dlg.get_task())
            self._persist()
            self._refresh_table()

    # ── refresh table — สร้าง checkbox ใหม่ทุกครั้ง ──────────
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

            # ── col 0 : checkbox (QPushButton) ────────────────
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
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 0px;
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
            cell0.setStyleSheet(
                f"background-color: {DONE_ROW_BG if done else WHITE};"
            )
            h0 = QHBoxLayout(cell0)
            h0.addWidget(chk)
            h0.setAlignment(Qt.AlignCenter)
            h0.setContentsMargins(4, 4, 4, 4)
            h0.setSpacing(0)
            self.table.setCellWidget(r, 0, cell0)

            # ── col 1 : status ────────────────────────────────
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor(STATUS_COLOR.get(status, DARK_COLOR)))
            status_item.setBackground(row_bg)
            self.table.setItem(r, 1, status_item)

            # ── col 2 : task name ─────────────────────────────
            name_item = QTableWidgetItem(task["name"])
            if done:
                f = name_item.font()
                f.setStrikeOut(True)
                name_item.setFont(f)
            name_item.setForeground(row_fg)
            name_item.setBackground(row_bg)
            self.table.setItem(r, 2, name_item)

            # ── col 3 : due date ──────────────────────────────
            due_str = task["due_dt"].strftime("%d %b, %Y %H:%M")
            date_item = QTableWidgetItem(due_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setForeground(row_fg)
            date_item.setBackground(row_bg)
            self.table.setItem(r, 3, date_item)

            # ── col 4 : edit / delete ─────────────────────────
            action_w = QWidget()
            action_w.setStyleSheet(
                f"background-color: {DONE_ROW_BG if done else WHITE};"
            )
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

        # clear empty rows
        for r in range(n, rows):
            for c in range(5):
                self.table.removeCellWidget(r, c)
                self.table.setItem(r, c, QTableWidgetItem(""))

        self._rebuilding = False

    # ── checkbox handler ──────────────────────────────────────
    def _on_checkbox(self, index: int, checked: bool):
        if index >= len(self._tasks):
            return
        self._tasks[index]["done"] = checked
        # ถ้าติ๊กเสร็จ → ย้ายไปท้ายสุด / ถ้า untick → ย้ายขึ้นบนสุด
        task = self._tasks.pop(index)
        if checked:
            self._tasks.append(task)       # done → ล่างสุด
        else:
            self._tasks.insert(0, task)    # undone → บนสุด
        self._persist()
        QTimer.singleShot(0, self._refresh_table)

    # ── edit ──────────────────────────────────────────────────
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

    # ── delete ────────────────────────────────────────────────
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

    # ── persist ───────────────────────────────────────────────
    def _persist(self):
        if self._email:
            user_store.save_tasks(self._email, self._tasks)

    # ── save CSV ──────────────────────────────────────────────
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
        """sync _tasks order หลัง drag&drop"""
        if src >= len(self._tasks) or dst >= len(self._tasks):
            QTimer.singleShot(0, self._refresh_table)
            return
        task = self._tasks.pop(src)
        self._tasks.insert(dst, task)
        self._persist()
        QTimer.singleShot(0, self._refresh_table)