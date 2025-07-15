import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout,
    QLineEdit, QComboBox, QSizePolicy, QFrame, QAbstractItemView, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont, QPixmap, QGuiApplication
from logic import get_decrypted_vault, save_vault

def add_icon_to_lineedit(line_edit: QLineEdit, icon_path: str):
    icon_label = QLabel(line_edit)
    pixmap = QPixmap(icon_path)
    icon_label.setPixmap(pixmap.scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    icon_label.setContentsMargins(8, 0, 8, 0)
    icon_label.setStyleSheet("background: transparent;")
    icon_label.setFixedSize(34, 34)
    line_edit.setTextMargins(40, 0, 0, 0)
    icon_label.move(4, (line_edit.height() - icon_label.height()) // 2)
    icon_label.show()
    def adjust_icon_position(event):
        icon_label.move(4, (line_edit.height() - icon_label.height()) // 2)
        QLineEdit.resizeEvent(line_edit, event)
    line_edit.resizeEvent = adjust_icon_position

def check_password_strength(password: str):
    import re
    length = len(password)
    score = 0
    if re.search(r'[A-Z]', password): score += 1
    if re.search(r'[a-z]', password): score += 1
    if re.search(r'[0-9]', password): score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 1
    if length >= 12 and score >= 3:
        return "Strong"
    return "Weak"

class StarIconLabel(QLabel):
    def __init__(self, is_starred, row, toggle_callback, parent=None):
        super().__init__(parent)
        self.row = row
        self.toggle_callback = toggle_callback
        star_path = os.path.join("assets", "star.png" if is_starred else "unstar.png")
        pixmap = QPixmap(star_path)
        pixmap = pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(24, 24)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.toggle_callback(self.row)

class VaultViewerScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AegisVault - Vault Viewer")
        self.setMinimumSize(950, 560)
        self.setStyleSheet(self.main_style())

        self.vault_data = []
        self.filtered_data = []
        self.starred = set()

        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Top Bar: Search, Sort, Close ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for Application, Username, or Vault...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(self.search_style())
        self.search_input.textChanged.connect(self.apply_search_and_sort)
        add_icon_to_lineedit(self.search_input, os.path.join("assets", "search.png"))
        self.search_input.setMinimumWidth(340)
        top_bar.addWidget(self.search_input, 2)

        sort_combo_row = QHBoxLayout()
        sort_combo_row.setSpacing(0)
        sort_combo_row.setContentsMargins(0, 0, 0, 0)

        self.sort_combo = QComboBox()
        self.sort_combo.setEditable(False)
        self.sort_combo.setFixedHeight(38)
        self.sort_combo.setFixedWidth(220)
        self.sort_combo.setStyleSheet(self.combobox_style())
        self.sort_combo.addItems([
            "Application (A-Z)",
            "Application (Z-A)",
            "Username (A-Z)",
            "Username (Z-A)",
            "Vault (A-Z)",
            "Vault (Z-A)",
            "Date Added (Newest)",
            "Date Added (Oldest)"
        ])
        self.sort_combo.currentIndexChanged.connect(self.apply_search_and_sort)
        sort_combo_row.addWidget(self.sort_combo)

        self.filter_btn = QPushButton()
        self.filter_btn.setFixedHeight(38)
        self.filter_btn.setFixedWidth(38)
        self.filter_btn.setIcon(QIcon(os.path.join("assets", "filter.png")))
        self.filter_btn.setStyleSheet("background: transparent; border: none; margin-left: 4px;")
        self.filter_btn.clicked.connect(self.sort_combo.showPopup)
        sort_combo_row.addWidget(self.filter_btn)

        sort_combo_widget = QWidget()
        sort_combo_widget.setLayout(sort_combo_row)
        top_bar.addWidget(sort_combo_widget, 0)

        top_bar.addStretch(2)

        self.close_btn = QPushButton("Close")
        self.close_btn.setIcon(QIcon(os.path.join("assets", "close.png")))
        self.close_btn.setFixedHeight(38)
        self.close_btn.setFixedWidth(110)
        self.close_btn.setStyleSheet(self.button_style(close=True))
        self.close_btn.clicked.connect(self.close_vault_viewer)
        top_bar.addWidget(self.close_btn, 0)

        layout.addLayout(top_bar)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # <-- Added column for copy button
        self.table.setHorizontalHeaderLabels([
            "",  # Starred
            "Application",
            "Username",
            "Password",
            "",  # Copy icon
            "Vault",
            "Date Added",
            "Strength"
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(False)
        self.table.setStyleSheet(self.table_style())
        self.table.setFont(QFont("Segoe UI", 11))
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellDoubleClicked.connect(self.toggle_password_visibility)
        self.table.cellClicked.connect(self.handle_star_click)
        layout.addWidget(self.table)

        # --- Bottom bar with Refresh, Edit, Delete Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        self.refresh_btn = QPushButton("Refresh Vault")
        self.refresh_btn.setIcon(QIcon(os.path.join("assets", "refresh.png")))
        self.refresh_btn.setFixedHeight(40)
        self.refresh_btn.setFixedWidth(170)
        self.refresh_btn.setStyleSheet(self.button_style())
        self.refresh_btn.clicked.connect(self.load_vault_entries)
        btn_layout.addWidget(self.refresh_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setIcon(QIcon(os.path.join("assets", "delete.png")))
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setFixedWidth(170)
        self.delete_btn.setStyleSheet(self.button_style(close=True))
        self.delete_btn.clicked.connect(self.delete_selected_entry)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        self.load_vault_entries()

    def load_vault_entries(self):
        self.vault_data = get_decrypted_vault()
        for entry in self.vault_data:
            if "date_added" not in entry:
                entry["date_added"] = datetime.now().isoformat()
            if "id" not in entry:
                entry["id"] = f"{entry['username']}::{entry['app_name']}"
        self.apply_search_and_sort()

    def apply_search_and_sort(self):
        search_text = self.search_input.text().lower().strip()
        if search_text:
            self.filtered_data = [
                entry for entry in self.vault_data
                if search_text in entry["app_name"].lower()
                or search_text in entry["username"].lower()
                or search_text in entry["vault"].lower()
            ]
        else:
            self.filtered_data = self.vault_data.copy()
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:
            self.filtered_data.sort(key=lambda x: x["app_name"].lower())
        elif sort_index == 1:
            self.filtered_data.sort(key=lambda x: x["app_name"].lower(), reverse=True)
        elif sort_index == 2:
            self.filtered_data.sort(key=lambda x: x["username"].lower())
        elif sort_index == 3:
            self.filtered_data.sort(key=lambda x: x["username"].lower(), reverse=True)
        elif sort_index == 4:
            self.filtered_data.sort(key=lambda x: x["vault"].lower())
        elif sort_index == 5:
            self.filtered_data.sort(key=lambda x: x["vault"].lower(), reverse=True)
        elif sort_index == 6:
            self.filtered_data.sort(key=lambda x: x.get("date_added", ""), reverse=True)
        elif sort_index == 7:
            self.filtered_data.sort(key=lambda x: x.get("date_added", ""))
        self.populate_table()

    def populate_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.filtered_data))
        for row, entry in enumerate(self.filtered_data):
            unique_id = entry.get('id', f"{entry['username']}::{entry['app_name']}")
            is_starred = unique_id in self.starred
            star_label = StarIconLabel(is_starred, row, self.toggle_star)
            self.table.setCellWidget(row, 0, star_label)

            # Application (not editable)
            app_item = QTableWidgetItem(entry["app_name"])
            app_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 1, app_item)

            # Username (not editable)
            user_item = QTableWidgetItem(entry["username"])
            user_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 2, user_item)

            # Password (masked, toggle on double click)
            masked_password = "●" * max(len(entry["password"]), 8)
            pwd_item = QTableWidgetItem(masked_password)
            pwd_item.setData(Qt.UserRole, entry["password"])
            pwd_item.setData(Qt.UserRole + 1, "masked")
            pwd_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            date_str = entry.get("date_added", "")
            try:
                date_obj = datetime.fromisoformat(date_str)
            except Exception:
                date_obj = datetime.now()
            if datetime.now() - date_obj > timedelta(days=180):
                icon = QIcon(os.path.join("assets", "clock.png"))
                pwd_item.setIcon(icon)
            self.table.setItem(row, 3, pwd_item)

            # Copy button
            copy_btn = QPushButton()
            copy_btn.setFixedSize(30, 30)
            copy_btn.setIcon(QIcon(os.path.join("assets", "copy.png")))
            copy_btn.setStyleSheet("background: transparent; border: none;")
            copy_btn.setToolTip("Copy password")
            copy_btn.clicked.connect(lambda checked, r=row: self.copy_password_to_clipboard(r))
            self.table.setCellWidget(row, 4, copy_btn)

            # Vault (not editable)
            vault_item = QTableWidgetItem(entry["vault"])
            vault_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 5, vault_item)

            # Date Added (not editable)
            date_item = QTableWidgetItem(date_obj.strftime("%Y-%m-%d"))
            date_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 6, date_item)

            # Strength (not editable)
            strength = check_password_strength(entry["password"])
            icon_path = "strong.png" if strength == "Strong" else "weak.png"
            strength_item = QTableWidgetItem("")
            strength_item.setIcon(QIcon(os.path.join("assets", icon_path)))
            strength_item.setText(strength)
            strength_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 7, strength_item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.blockSignals(False)

    def copy_password_to_clipboard(self, row):
        if 0 <= row < len(self.filtered_data):
            password = self.filtered_data[row]["password"]
            QGuiApplication.clipboard().setText(password)
            QMessageBox.information(self, "Copied", "Password copied to clipboard!")

    def handle_star_click(self, row, column):
        if column == 0:
            self.toggle_star(row)

    def toggle_star(self, row):
        entry = self.filtered_data[row]
        unique_id = entry.get('id', f"{entry['username']}::{entry['app_name']}")
        if unique_id in self.starred:
            self.starred.remove(unique_id)
        else:
            self.starred.add(unique_id)
        self.populate_table()

    def toggle_password_visibility(self, row, column):
        if column == 3:
            item = self.table.item(row, column)
            real_pwd = item.data(Qt.UserRole)
            state = item.data(Qt.UserRole + 1)
            if state == "masked":
                item.setText(real_pwd)
                item.setData(Qt.UserRole + 1, "visible")
            else:
                masked_password = "●" * max(len(real_pwd), 8)
                item.setText(masked_password)
                item.setData(Qt.UserRole + 1, "masked")

    def delete_selected_entry(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.filtered_data):
            QMessageBox.information(self, "Delete Entry", "Please select a row to delete.")
            return
        confirm = QMessageBox.question(
            self, "Delete Entry",
            f"Are you sure you want to delete '{self.filtered_data[row]['app_name']}' for user '{self.filtered_data[row]['username']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            entry_id = self.filtered_data[row]['id']
            self.vault_data = [entry for entry in self.vault_data if entry['id'] != entry_id]
            self.filtered_data = [entry for entry in self.filtered_data if entry['id'] != entry_id]
            save_vault(self.vault_data)
            self.populate_table()

    def close_vault_viewer(self):
        if self.parent() and hasattr(self.parent(), "show_main_app_screen"):
            self.parent().show_main_app_screen()

    # --- Styles ---
    def main_style(self):
        return """
            QWidget {
                background: #344955;
            }
        """

    def search_style(self):
        return """
            QLineEdit {
                border: 2px solid #50727B;
                border-radius: 8px;
                padding-left: 8px;
                font-size: 15px;
                background: #35374B;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #78A083;
                background: #35374B;
            }
        """

    def combobox_style(self):
        return """
            QComboBox {
                border: 2px solid #50727B;
                border-radius: 8px;
                padding: 4px 12px;
                font-size: 15px;
                background: #35374B;
                color: #FFFFFF;
            }
            QComboBox:focus {
                border: 2px solid #78A083;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #344955;
                color: #FFFFFF;
                selection-background-color: #50727B;
                selection-color: #78A083;
            }
        """

    def table_style(self):
        return """
            QTableWidget {
                background: #35374B;
                border-radius: 10px;
                border: 2px solid #50727B;
                gridline-color: #50727B;
                alternate-background-color: #344955;
                color: #FFF;
            }
            QHeaderView::section {
                background-color: #50727B;
                color: #78A083;
                font-size: 15px;
                font-weight: bold;
                border: none;
                padding: 6px 0;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background: #78A083;
                color: #35374B;
            }
        """

    def button_style(self, close=False):
        if close:
            return """
                QPushButton {
                    background-color: #35374B;
                    color: #78A083;
                    border-radius: 10px;
                    font-size: 15px;
                    font-weight: 600;
                    border: 2px solid #78A083;
                    padding: 0 14px;
                }
                QPushButton:hover {
                    background-color: #78A083;
                    color: #35374B;
                    border: 2px solid #50727B;
                }
                QPushButton:pressed {
                    background-color: #50727B;
                    color: #78A083;
                }
            """
        return """
            QPushButton {
                background-color: #50727B;
                color: #FFFFFF;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                border: 2px solid #78A083;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #78A083;
                border: 2px solid #50727B;
                color: #35374B;
            }
            QPushButton:pressed {
                background-color: #35374B;
                color: #78A083;
            }
        """

    def icon_button_style(self):
        return """
            QPushButton {
                background-color: #35374B;
                border: 2px solid #50727B;
                border-radius: 8px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #78A083;
                border: 2px solid #50727B;
            }
            QPushButton:pressed {
                background-color: #50727B;
            }
        """