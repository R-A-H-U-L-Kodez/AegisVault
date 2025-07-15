from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from logic import generate_password, add_password_entry, get_decrypted_vault


class PasswordInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password (or Generate)")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_btn = QPushButton("Show")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFixedWidth(60)
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)

        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.toggle_btn)
        self.setLayout(self.layout)

    def toggle_password_visibility(self):
        if self.toggle_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("Show")

    def text(self):
        return self.password_input.text()

    def setText(self, text):
        self.password_input.setText(text)

    def clear(self):
        self.password_input.clear()


class VaultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AegisVault - Saved Passwords")
        self.setGeometry(150, 150, 650, 400)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.vault_table = QTableWidget()
        self.vault_table.setColumnCount(3)
        self.vault_table.setHorizontalHeaderLabels(["Application", "Username", "Password"])
        self.vault_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vault_table.setAlternatingRowColors(True)

        self.layout.addWidget(self.vault_table)
        self.setLayout(self.layout)

        self.load_vault()

    def load_vault(self):
        vault = get_decrypted_vault()
        self.vault_table.setRowCount(len(vault))
        for row, entry in enumerate(vault):
            self.vault_table.setItem(row, 0, QTableWidgetItem(entry["app_name"]))
            self.vault_table.setItem(row, 1, QTableWidgetItem(entry["username"]))
            self.vault_table.setItem(row, 2, QTableWidgetItem(entry["password"]))


class AegisVaultApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AegisVault - Password Manager")
        self.setGeometry(100, 100, 600, 280)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(12)

        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Input Fields
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("Application Name")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_widget = PasswordInputWidget()

        # Apply consistent styling to inputs with grey background and placeholder grey text
        for widget in (self.app_input, self.username_input, self.password_widget.password_input):
            widget.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1.5px solid #ccc;
                    border-radius: 6px;
                    background: #f0f0f0;
                    color: #333;
                }
                QLineEdit:placeholder {
                    color: #888888;
                }
                QLineEdit:focus {
                    border-color: #4A90E2;
                    background: #ffffff;
                    color: #000000;
                }
            """)

        self.layout.addWidget(self.app_input)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_widget)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.generate_btn = QPushButton("Generate Password")
        self.add_btn = QPushButton("Add Entry")
        self.view_vault_btn = QPushButton("View Vault")

        for btn in (self.generate_btn, self.add_btn, self.view_vault_btn):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 6px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
                QPushButton:pressed {
                    background-color: #2A5F9E;
                }
            """)

        self.generate_btn.clicked.connect(self.generate_password)
        self.add_btn.clicked.connect(self.add_entry)
        self.view_vault_btn.clicked.connect(self.open_vault_window)

        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.view_vault_btn)

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)
        self.vault_window = None

    def generate_password(self):
        pwd = generate_password()
        self.password_widget.setText(pwd)

    def add_entry(self):
        app_name = self.app_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_widget.text().strip()

        if not app_name or not username or not password:
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return

        add_password_entry(app_name, username, password)
        QMessageBox.information(self, "Success", "Password entry added successfully!")

        self.app_input.clear()
        self.username_input.clear()
        self.password_widget.clear()

        if self.vault_window and self.vault_window.isVisible():
            self.vault_window.load_vault()

    def open_vault_window(self):
        if self.vault_window is None:
            self.vault_window = VaultWindow()
        self.vault_window.load_vault()
        self.vault_window.show()
