from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QFileDialog, QMenuBar, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QFont

TOPBAR_COLOR = "#3b82f6"   # top bar + table header + buttons
TITLE_COLOR  = "#1e293b"   # "OnTrack" text only
BG_COLOR     = "#EEF2F5"
DARK_COLOR   = "#1e293b"
WHITE        = "#FFFFFF"


class TaskPage(QWidget):
    go_to_login = Signal()

    def __init__(self, username: str = "", parent=None):
        super().__init__(parent)
        self.username = username
        self._build_ui()

    def set_username(self, username: str):
        self.username = username
        self.user_label.setText(username)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Title bar (Save File menu) ────────────────────────
        title_bar = QWidget()
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #ccc;")
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(4, 0, 8, 0)
        tb_layout.setSpacing(0)

        menu_bar = QMenuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: transparent;
                color: #1e293b;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMenuBar::item { background: transparent; padding: 4px 10px; }
            QMenuBar::item:selected { background-color: #d0d7e2; border-radius: 4px; }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #D0D7E2;
                font-size: 13px;
                color: #1e293b;
            }
            QMenu::item { padding: 7px 24px; }
            QMenu::item:selected { background-color: #EEF2F5; }
        """)

        save_menu = QMenu("💾  Save File", menu_bar)
        act_table = QAction("🗂  Save Table", self)
        act_table.triggered.connect(self._save_table)
        act_graph = QAction("📊  Save Graph", self)
        act_graph.triggered.connect(self._save_graph)
        save_menu.addAction(act_table)
        save_menu.addAction(act_graph)
        menu_bar.addMenu(save_menu)

        tb_layout.addWidget(menu_bar)
        tb_layout.addStretch()
        root.addWidget(title_bar)

        # ── Top bar ───────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_bar.setStyleSheet(f"background-color: {TOPBAR_COLOR};")

        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 0, 0, 0)
        top_layout.setSpacing(0)

        app_title = QLabel("OnTrack")
        app_title.setStyleSheet(
            f"font-size: 24px; font-weight: 800; color: {TITLE_COLOR};"
            f"background-color: {TOPBAR_COLOR}; font-family: 'Segoe UI', Arial, sans-serif;"
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

        logout_btn = QPushButton("⇥")
        logout_btn.setToolTip("Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setFixedSize(44, 60)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {TOPBAR_COLOR};
                border: none; color: {WHITE}; font-size: 18px;
            }}
            QPushButton:hover {{ background-color: #2563eb; }}
        """)
        logout_btn.clicked.connect(self._do_logout)

        top_layout.addWidget(user_icon)
        top_layout.addWidget(self.user_label)
        top_layout.addSpacing(8)
        top_layout.addWidget(logout_btn)
        root.addWidget(top_bar)

        # ── Content ───────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_COLOR};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(14)

        # Header row
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

        # + / 📊 buttons
        btn_col = QVBoxLayout()
        btn_col.setSpacing(4)
        btn_col.setAlignment(Qt.AlignRight)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.setAlignment(Qt.AlignRight)

        add_btn = QPushButton("+")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedSize(46, 46)
        add_btn.setFont(QFont("Segoe UI", 20, QFont.Black))
        # AlignCenter ให้ข้อความอยู่กึ่งกลางจริงๆ
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {TOPBAR_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0px;
                text-align: center;
                qproperty-iconSize: 0px;
            }}
            QPushButton:hover {{ background-color: #2563eb; }}
        """)

        graph_btn = QPushButton("📊")
        graph_btn.setCursor(Qt.PointingHandCursor)
        graph_btn.setFixedSize(46, 46)
        graph_btn.setFont(QFont("Segoe UI", 18))
        graph_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {TOPBAR_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0px;
                text-align: center;
            }}
            QPushButton:hover {{ background-color: #2563eb; }}
        """)

        btn_row.addWidget(add_btn)
        btn_row.addWidget(graph_btn)

        add_label = QLabel("Add Task here!")
        add_label.setAlignment(Qt.AlignCenter)
        add_label.setStyleSheet(
            "font-size:11px; color:#5A6478; font-family:'Segoe UI',Arial,sans-serif;"
        )
        btn_col.addLayout(btn_row)
        btn_col.addWidget(add_label)
        header_row.addLayout(btn_col)
        cl.addLayout(header_row)

        # ── Table ─────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "Status", "Task Name", "Due Date"])
        self.table.setRowCount(8)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {WHITE};
                border: 1.5px solid #D0D7E2;
                border-radius: 10px;
                gridline-color: #E4EAF2;
                font-size: 13px;
                color: {DARK_COLOR};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QTableWidget::item {{ padding: 8px 10px; border: none; }}
            QTableWidget::item:selected {{
                background-color: #dbeafe; color: {DARK_COLOR};
            }}
            QHeaderView::section {{
                background-color: {TOPBAR_COLOR};
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 8px;
                border: none;
            }}
            QHeaderView::section:first {{ border-top-left-radius: 8px; }}
            QHeaderView::section:last  {{ border-top-right-radius: 8px; }}
        """)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 36)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 90)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 160)

        for r in range(8):
            self.table.setRowHeight(r, 44)

        cl.addWidget(self.table)
        root.addWidget(content)

    # ── Slots ─────────────────────────────────────────────────
    def _save_table(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Table", "my_tasks", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Status,Task Name,Due Date\n")
                for row in range(self.table.rowCount()):
                    name = self.table.item(row, 2)
                    if name and name.text().strip():
                        s = (self.table.item(row, 1) or QTableWidgetItem("")).text()
                        d = (self.table.item(row, 3) or QTableWidgetItem("")).text()
                        f.write(f"{s},{name.text()},{d}\n")
        except Exception as e:
            self._show_err(str(e))

    def _save_graph(self):
        from styles import styled_msgbox
        from PySide6.QtWidgets import QMessageBox
        styled_msgbox(self, "Save Graph",
                      "Graph export is not available yet.",
                      QMessageBox.Information).exec()

    def _show_err(self, msg):
        from styles import styled_msgbox
        from PySide6.QtWidgets import QMessageBox
        styled_msgbox(self, "Save Error", msg, QMessageBox.Warning).exec()

    def _do_logout(self):
        self.go_to_login.emit()