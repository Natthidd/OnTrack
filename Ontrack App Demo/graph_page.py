from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from PySide6.QtCore import Qt, QRectF, QTimer, Signal
from PySide6.QtGui import (
    QColor, QFont, QLinearGradient, QPainter, QPainterPath,
    QPen, QPixmap,
)
import os

from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

import user_store

# ── palette (same blue/navy as the rest of the app) ───────────────────────────
TOPBAR   = "#3b82f6"
NAVY     = "#1e293b"
BG       = "#EEF2F5"
WHITE    = "#FFFFFF"
SUCCESS  = "#10b981"
OVERDUE  = "#E05252"
DUE_TODAY= "#f59e0b"
UPCOMING = "#3b82f6"

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

# colours for each category bar segment
CAT_COLORS = {
    "Homework": "#3b82f6",
    "Exam":     "#8b5cf6",
    "Reading":  "#06b6d4",
    "Exercise": "#10b981",
    "Other":    "#f59e0b",
}
# colour for status bars
STATUS_COLORS = {
    "Success":   SUCCESS,
    "Overdue":   OVERDUE,
    "Due Today": DUE_TODAY,
    "Upcoming":  UPCOMING,
}


def _month_key(dt: datetime) -> tuple[int, int]:
    return dt.year, dt.month


# ── Donut widget ───────────────────────────────────────────────────────────────
class DonutWidget(QWidget):
    """Small donut chart showing task completion ratio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self._done  = 0
        self._total = 0

    def set_data(self, done: int, total: int):
        self._done  = done
        self._total = total
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        r = QRectF(10, 10, 100, 100)
        pen_w = 18

        # background ring
        p.setPen(QPen(QColor("#D0D7E2"), pen_w, Qt.SolidLine, Qt.FlatCap))
        p.drawArc(r, 0, 360 * 16)

        # filled arc
        if self._total > 0:
            frac = self._done / self._total
            span = int(frac * 360 * 16)
            p.setPen(QPen(QColor(SUCCESS), pen_w, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(r, 90 * 16, -span)

        # centre text
        p.setPen(QColor(NAVY))
        pct = int(self._done / self._total * 100) if self._total else 0
        p.setFont(QFont("Segoe UI", 15, QFont.Bold))
        p.drawText(r, Qt.AlignCenter, f"{pct}%")
        p.end()


# ── Bar-chart widget ───────────────────────────────────────────────────────────
class BarChartWidget(QWidget):
    """Stacked bar chart — one bar per month for the selected year."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(200)
        # data: list of 12 dicts {label->count}  (index 0 = Jan)
        self._bars: list[dict[str, int]] = [{} for _ in range(12)]
        self._color_map: dict[str, str]  = {}
        self._title = ""

    def set_data(self,
                 bars: list[dict[str, int]],
                 color_map: dict[str, str],
                 title: str = ""):
        self._bars      = bars
        self._color_map = color_map
        self._title     = title
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        W = self.width()
        H = self.height()
        pad_l, pad_r, pad_t, pad_b = 48, 16, 32, 36

        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b

        # max value
        max_val = max((sum(b.values()) for b in self._bars), default=1) or 1

        bar_w    = chart_w / 12
        bar_gap  = bar_w * 0.25
        bar_body = bar_w - bar_gap

        # ── grid lines ────────────────────────────────────────
        p.setPen(QPen(QColor("#E4EAF2"), 1, Qt.DashLine))
        steps = 5
        for i in range(steps + 1):
            y = pad_t + chart_h - (i / steps) * chart_h
            p.drawLine(pad_l, int(y), W - pad_r, int(y))
            # y-axis labels
            p.setPen(QColor("#9ca3af"))
            p.setFont(QFont("Segoe UI", 8))
            label = str(int(max_val * i / steps))
            p.drawText(0, int(y) - 6, pad_l - 4, 14,
                       Qt.AlignRight | Qt.AlignVCenter, label)
            p.setPen(QPen(QColor("#E4EAF2"), 1, Qt.DashLine))

        # ── bars ──────────────────────────────────────────────
        for m in range(12):
            bx = pad_l + m * bar_w + bar_gap / 2
            data = self._bars[m]
            total = sum(data.values())

            y_top = pad_t + chart_h   # start from bottom
            for label, count in data.items():
                if count <= 0:
                    continue
                bar_h = (count / max_val) * chart_h
                y_top -= bar_h
                color = QColor(self._color_map.get(label, "#94a3b8"))

                # gradient fill
                grad = QLinearGradient(bx, y_top, bx, y_top + bar_h)
                grad.setColorAt(0, color.lighter(115))
                grad.setColorAt(1, color)
                p.setBrush(grad)
                p.setPen(Qt.NoPen)

                rect = QRectF(bx, y_top, bar_body, bar_h)
                path = QPainterPath()
                if y_top == pad_t + chart_h - (count / max_val) * chart_h:
                    # bottom-most segment — round bottom
                    path.addRoundedRect(rect, 4, 4)
                else:
                    path.addRect(rect)
                p.drawPath(path)

            # month label
            p.setPen(QColor(NAVY))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(int(bx), H - pad_b + 4, int(bar_body), 20,
                       Qt.AlignCenter, MONTH_NAMES[m])

            # value on top
            if total > 0:
                p.setPen(QColor(NAVY))
                p.setFont(QFont("Segoe UI", 8, QFont.Bold))
                bar_top_y = pad_t + chart_h - (total / max_val) * chart_h
                p.drawText(int(bx), int(bar_top_y) - 16, int(bar_body), 14,
                           Qt.AlignCenter, str(total))

        p.end()


# ── Legend widget ──────────────────────────────────────────────────────────────
class LegendWidget(QWidget):
    def __init__(self, items: dict[str, str], parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addStretch()
        for label, color in items.items():
            dot = QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(
                f"background:{color}; border-radius:6px;"
            )
            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"font-size:12px; color:{NAVY};"
                "font-family:'Segoe UI',Arial,sans-serif;"
            )
            layout.addWidget(dot)
            layout.addWidget(lbl)
        layout.addStretch()


# ── Stat card ──────────────────────────────────────────────────────────────────
class StatCard(QWidget):
    def __init__(self, icon: str, label: str, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedHeight(72)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {WHITE};
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:22px; background:transparent; border:none;")
        icon_lbl.setFixedWidth(32)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)

        self.number_lbl = QLabel("0")
        self.number_lbl.setStyleSheet(
            f"font-size:20px; font-weight:700; color:{NAVY};"
            "background:transparent; border:none;"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )

        desc_lbl = QLabel(label)
        desc_lbl.setStyleSheet(
            f"font-size:11px; color:#5A6478; background:transparent; border:none;"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )

        text_col.addWidget(self.number_lbl)
        text_col.addWidget(desc_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col)
        layout.addStretch()

    def set_value(self, v: int):
        self.number_lbl.setText(str(v))


# ── Graph Page ─────────────────────────────────────────────────────────────────
class GraphPage(QWidget):
    go_to_task = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._email  = ""
        self._tasks: list[dict] = []
        self._year   = datetime.now().year
        self._mode   = "category"   # "category" | "status"
        self._build_ui()

    # ── public ────────────────────────────────────────────────
    def set_user(self, email: str):
        self._email = email
        self.refresh()

    def refresh(self):
        if self._email:
            self._tasks = user_store.load_tasks(self._email)
        self._rebuild()

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color:{BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── top bar ───────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet(f"background-color:{TOPBAR};")
        tl = QHBoxLayout(top_bar)
        tl.setContentsMargins(16, 0, 16, 0)

        app_lbl = QLabel("OnTrack")
        app_lbl.setStyleSheet(
            f"font-size:24px; font-weight:800; color:{NAVY};"
            f"background:{TOPBAR}; font-family:'Segoe UI',Arial,sans-serif;"
        )
        tl.addWidget(app_lbl)
        tl.addStretch()

        back_btn = QPushButton("← Back")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedHeight(36)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255,255,255,0.2); color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 600; padding: 0 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{ background-color: rgba(255,255,255,0.35); }}
        """)
        back_btn.clicked.connect(self.go_to_task.emit)
        tl.addWidget(back_btn)

        # ── Save Graph button ──────────────────────────────────
        # Placed next to Back button in the top bar.
        # Clicking it opens a file-save dialog so the user can
        # export the current graph view as a PNG image.
        save_btn = QPushButton("💾 Save Graph")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255,255,255,0.2); color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 600; padding: 0 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{ background-color: rgba(255,255,255,0.35); }}
        """)
        save_btn.clicked.connect(self._save_graph)
        tl.addWidget(save_btn)

        root.addWidget(top_bar)

        # ── scrollable content ────────────────────────────────
        content = QWidget()
        content.setStyleSheet(f"background-color:{BG};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(16)

        # heading row
        h_row = QHBoxLayout()
        title_lbl = QLabel("My Graph")
        title_lbl.setStyleSheet(
            f"font-size:20px; font-weight:700; color:{NAVY};"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )
        sub_lbl = QLabel("Monthly task overview")
        sub_lbl.setStyleSheet(
            "font-size:13px; color:#5A6478;"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )

        sub_lbl2 = QLabel("Don't stop until you're proud. Keep going!")
        sub_lbl2.setStyleSheet(
            "font-size:13px; color:#5A6478;"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        title_col.addWidget(sub_lbl2)
        h_row.addLayout(title_col)
        h_row.addStretch()

        # year selector
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for y in range(current_year - 50, current_year + 50):
            self.year_combo.addItem(str(y))
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.setFixedHeight(34)
        self.year_combo.setStyleSheet(f"""
            QComboBox {{
                color: black;
                background-color: {WHITE};
                border: 1.5px solid #D0D7E2;
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
             QComboBox QAbstractItemView {{
                color: black;
                background-color: {WHITE};
                selection-background-color: #cce5ff;
                selection-color: black;
            }}
        """)
        self.year_combo.currentTextChanged.connect(self._on_year_changed)
        h_row.addWidget(self.year_combo)
        cl.addLayout(h_row)

        # ── stat cards ────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)
        self.card_total    = StatCard("📋", "Total Tasks",    TOPBAR)
        self.card_done     = StatCard("✅", "Completed",      SUCCESS)
        self.card_overdue  = StatCard("⚠️", "Overdue",        OVERDUE)
        self.card_upcoming = StatCard("🕐", "Upcoming",       UPCOMING)
        for c in (self.card_total, self.card_done,
                  self.card_overdue, self.card_upcoming):
            cards_row.addWidget(c)
        cl.addLayout(cards_row)

        # ── donut + bar chart side by side ────────────────────
        charts_row = QHBoxLayout()
        charts_row.setSpacing(12)

        # donut card
        donut_card = QWidget()
        donut_card.setStyleSheet(f"""
            QWidget {{
                background-color:{WHITE}; border-radius:14px;
            }}
        """)
        donut_card.setFixedWidth(156)
        dc_layout = QVBoxLayout(donut_card)
        dc_layout.setContentsMargins(12, 16, 12, 12)
        dc_layout.setSpacing(6)
        donut_title = QLabel("Completion")
        donut_title.setAlignment(Qt.AlignCenter)
        donut_title.setStyleSheet(
            f"font-size:13px; font-weight:600; color:{NAVY};"
            "background:transparent;"
        )
        dc_layout.addWidget(donut_title)
        self.donut = DonutWidget()
        dc_layout.addWidget(self.donut, alignment=Qt.AlignCenter)
        done_sub = QLabel("Tasks done this year")
        done_sub.setAlignment(Qt.AlignCenter)
        done_sub.setWordWrap(True)
        done_sub.setStyleSheet(
            "font-size:11px; color:#5A6478; background:transparent;"
        )
        dc_layout.addWidget(done_sub)
        dc_layout.addStretch()
        charts_row.addWidget(donut_card)

        # bar chart card
        bar_card = QWidget()
        bar_card.setStyleSheet(f"""
            QWidget {{ background-color:{WHITE}; border-radius:14px; }}
        """)
        bar_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bc_layout = QVBoxLayout(bar_card)
        bc_layout.setContentsMargins(16, 16, 16, 10)
        bc_layout.setSpacing(8)

        # mode toggle
        mode_row = QHBoxLayout()
        bar_title_lbl = QLabel("Tasks per Month")
        bar_title_lbl.setStyleSheet(
            f"font-size:13px; font-weight:700; color:{NAVY}; background:transparent;"
        )
        mode_row.addWidget(bar_title_lbl)
        mode_row.addStretch()

        self.mode_cat_btn = QPushButton("By Category")
        self.mode_sts_btn = QPushButton("By Status")
        for btn, mode in ((self.mode_cat_btn, "category"),
                          (self.mode_sts_btn, "status")):
            btn.setFixedHeight(26)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, m=mode: self._set_mode(m))
            mode_row.addWidget(btn)
        bc_layout.addLayout(mode_row)

        self.bar_chart = BarChartWidget()
        self.bar_chart.setMinimumHeight(180)
        bc_layout.addWidget(self.bar_chart)

        self.legend_widget = QWidget()
        self.legend_layout = QHBoxLayout(self.legend_widget)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        bc_layout.addWidget(self.legend_widget)

        charts_row.addWidget(bar_card)
        cl.addLayout(charts_row)

        # ── category/status breakdown ─────────────────────────
        self.breakdown_title = QLabel("Category Breakdown (this year)")
        self.breakdown_title.setStyleSheet(
            f"font-size:14px; font-weight:700; color:{NAVY};"
            "font-family:'Segoe UI',Arial,sans-serif;"
        )
        cl.addWidget(self.breakdown_title)

        self.breakdown_row = QHBoxLayout()
        self.breakdown_row.setSpacing(10)
        cl.addLayout(self.breakdown_row)

        cl.addStretch()
        root.addWidget(content)

        # init mode styles
        self._set_mode("category")

    # ── save graph ────────────────────────────────────────────
    def _save_graph(self):
        """
        Capture the entire GraphPage widget as a PNG image and let
        the user choose where to save it via a file-save dialog.

        Steps:
        1. Open QFileDialog to pick the destination file path.
        2. Grab the widget's current rendered pixels with QWidget.grab().
           This renders exactly what is visible on screen (bar chart,
           donut, stat cards, legend, breakdown) into a QPixmap.
        3. Save the QPixmap to the chosen path as PNG.
        4. Show a success or error message box.
        """
        # Default filename includes mode and year for easy identification
        default_name = f"graph_{self._mode}_{self._year}.png"

        # Suggest saving inside a "graphs" subfolder next to the script
        graphs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs")
        os.makedirs(graphs_dir, exist_ok=True)
        default_path = os.path.join(graphs_dir, default_name)

        # Open save-file dialog filtered to PNG only
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Graph as Image",
            default_path,
            "PNG Image (*.png)"
        )

        if not file_path:
            # User cancelled the dialog — do nothing
            return

        # Ensure the file has a .png extension
        if not file_path.lower().endswith(".png"):
            file_path += ".png"

        # Grab the current visual state of this widget into a QPixmap
        pixmap = self.grab()

        # Save to disk
        if pixmap.save(file_path, "PNG"):
            from styles import styled_msgbox
            styled_msgbox(
                self,
                "Graph Saved",
                f"Graph saved successfully!\n{file_path}",
                QMessageBox.Information
            ).exec()
        else:
            from styles import styled_msgbox
            styled_msgbox(
                self,
                "Save Failed",
                "Could not save the graph. Please try again.",
                QMessageBox.Warning
            ).exec()

    # ── mode toggle ───────────────────────────────────────────
    def _set_mode(self, mode: str):
        self._mode = mode
        active_style = f"""
            QPushButton {{
                background-color:{TOPBAR}; color:white;
                border:none; border-radius:6px;
                font-size:11px; font-weight:700; padding:2px 10px;
            }}
        """
        inactive_style = f"""
            QPushButton {{
                background-color:#EEF2F5; color:{NAVY};
                border:1.5px solid #D0D7E2; border-radius:6px;
                font-size:11px; padding:2px 10px;
            }}
            QPushButton:hover {{ background-color:#dbeafe; }}
        """
        self.mode_cat_btn.setStyleSheet(
            active_style if mode == "category" else inactive_style
        )
        self.mode_sts_btn.setStyleSheet(
            active_style if mode == "status" else inactive_style
        )
        self._rebuild()

    def _on_year_changed(self, text: str):
        try:
            self._year = int(text)
        except ValueError:
            pass
        self._rebuild()

    # ── data ─────────────────────────────────────────────────
    def _rebuild(self):
        year = self._year
        tasks_year = [
            t for t in self._tasks
            if isinstance(t.get("due_dt"), datetime) and t["due_dt"].year == year
        ]

        # stat cards
        total    = len(tasks_year)
        done     = sum(1 for t in tasks_year if t.get("done"))
        now      = datetime.now()
        overdue  = sum(
            1 for t in tasks_year
            if not t.get("done") and t["due_dt"] < now
        )
        upcoming = total - done - overdue

        self.card_total.set_value(total)
        self.card_done.set_value(done)
        self.card_overdue.set_value(overdue)
        self.card_upcoming.set_value(upcoming)

        # donut
        self.donut.set_data(done, total)

        # bar chart
        if self._mode == "category":
            bars = [{} for _ in range(12)]
            for t in tasks_year:
                m  = t["due_dt"].month - 1
                cat = t.get("category", "Other")
                bars[m][cat] = bars[m].get(cat, 0) + 1
            color_map = CAT_COLORS
        else:
            bars = [{} for _ in range(12)]
            for t in tasks_year:
                m = t["due_dt"].month - 1
                if t.get("done"):
                    key = "Success"
                elif t["due_dt"].date() == now.date():
                    key = "Due Today"
                elif t["due_dt"] < now:
                    key = "Overdue"
                else:
                    key = "Upcoming"
                bars[m][key] = bars[m].get(key, 0) + 1
            color_map = STATUS_COLORS

        self.bar_chart.set_data(bars, color_map)

        # rebuild legend
        for i in reversed(range(self.legend_layout.count())):
            w = self.legend_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        self.legend_layout.addStretch()
        for label, color in color_map.items():
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(
                f"background:{color}; border-radius:5px; border:none;"
            )
            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"font-size:11px; color:{NAVY}; background:transparent;"
                "font-family:'Segoe UI',Arial,sans-serif;"
            )
            self.legend_layout.addWidget(dot)
            self.legend_layout.addWidget(lbl)
        self.legend_layout.addStretch()

        # rebuild breakdown mini-bars (changes with mode)
        for i in reversed(range(self.breakdown_row.count())):
            item = self.breakdown_row.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        if self._mode == "category":
            self.breakdown_title.setText("Category Breakdown (this year)")
            cat_totals: dict[str, int] = defaultdict(int)
            for t in tasks_year:
                cat_totals[t.get("category", "Other")] += 1
            breakdown_items = [
                (cat, cat_totals.get(cat, 0), CAT_COLORS.get(cat, "#94a3b8"))
                for cat in ["Homework", "Exam", "Reading", "Exercise", "Other"]
            ]
        else:
            self.breakdown_title.setText("Status Breakdown (this year)")
            status_totals: dict[str, int] = defaultdict(int)
            for t in tasks_year:
                if t.get("done"):
                    sk = "Success"
                elif t["due_dt"].date() == now.date():
                    sk = "Due Today"
                elif t["due_dt"] < now:
                    sk = "Overdue"
                else:
                    sk = "Upcoming"
                status_totals[sk] += 1
            breakdown_items = [
                (s, status_totals.get(s, 0), STATUS_COLORS.get(s, "#94a3b8"))
                for s in ["Success", "Overdue", "Due Today", "Upcoming"]
            ]

        if not any(c for _, c, _ in breakdown_items):
            empty_lbl = QLabel("No tasks found for this year.")
            empty_lbl.setStyleSheet(
                "font-size:13px; color:#9ca3af; background:transparent;"
            )
            self.breakdown_row.addWidget(empty_lbl)
            return

        max_val2 = max((c for _, c, _ in breakdown_items), default=1) or 1

        for label, count, color in breakdown_items:
            mini = QWidget()
            mini.setStyleSheet(f"""
                QWidget {{
                    background-color:{WHITE};
                    border-radius:10px;
                    border-left: 4px solid {color};
                }}
            """)
            mini.setFixedHeight(72)
            mini.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            ml = QVBoxLayout(mini)
            ml.setContentsMargins(10, 8, 10, 8)
            ml.setSpacing(4)

            top_row = QHBoxLayout()
            cat_lbl = QLabel(label)
            cat_lbl.setStyleSheet(
                f"font-size:12px; font-weight:600; color:{NAVY};"
                "background:transparent; border:none;"
            )
            cnt_lbl = QLabel(str(count))
            cnt_lbl.setStyleSheet(
                f"font-size:14px; font-weight:700; color:{color};"
                "background:transparent; border:none;"
            )
            top_row.addWidget(cat_lbl)
            top_row.addStretch()
            top_row.addWidget(cnt_lbl)
            ml.addLayout(top_row)

            bar_bg = QWidget()
            bar_bg.setFixedHeight(6)
            bar_bg.setStyleSheet(
                "background-color:#E4EAF2; border-radius:3px; border:none;"
            )
            bar_bg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            frac = count / max_val2 if max_val2 else 0
            bar_fill = QWidget(bar_bg)
            bar_fill.setStyleSheet(
                f"background-color:{color}; border-radius:3px;"
            )
            bar_fill.setFixedHeight(6)
            bar_bg._frac = frac
            bar_bg._fill = bar_fill

            def _resize(event, bg=bar_bg):
                bg._fill.setFixedWidth(max(4, int(bg.width() * bg._frac)))
                bg._fill.move(0, 0)

            bar_bg.resizeEvent = _resize
            ml.addWidget(bar_bg)

            self.breakdown_row.addWidget(mini)