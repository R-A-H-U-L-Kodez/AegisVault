from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMainWindow, QStackedWidget
)
from PySide6.QtGui import QIcon


class MainWindowUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AegisVault - Password Manager")
        self.setMinimumSize(700, 500)

        self.layout = QVBoxLayout(self)

        # ---------------- Search Bar ----------------
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        search_layout.addWidget(self.search_input)

        self.layout.addLayout(search_layout)

        # ---------------- Input Fields ----------------
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("Application Name")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password (or Generate)")
        self.password_input.setEchoMode(QLineEdit.Password)  # Masked by default

        self.layout.addWidget(self.app_input)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)

        # ---------------- Buttons Layout ----------------
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Generate Password")
        button_layout.addWidget(self.generate_btn)

        self.toggle_pwd_btn = QPushButton("Show/Hide")
        button_layout.addWidget(self.toggle_pwd_btn)

        self.add_btn = QPushButton("Add Entry")
        button_layout.addWidget(self.add_btn)

        self.layout.addLayout(button_layout)

        # ---------------- Vault Table ----------------
        self.vault_table = QTableWidget()
        self.vault_table.setColumnCount(4)
        self.vault_table.setHorizontalHeaderLabels(["App", "Username", "Password", "Reveal"])
        self.vault_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.vault_table)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AegisVault")
        self.setMinimumSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Import your screens
        from login_screen import LoginScreen
        from main_app_screen import MainAppScreen
        from vault_viewer import VaultViewerScreen

        self.login_screen = LoginScreen(parent=self)
        self.main_app_screen = MainAppScreen(parent=self)
        self.vault_viewer_screen = VaultViewerScreen(parent=self)

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.main_app_screen)
        self.stack.addWidget(self.vault_viewer_screen)

        # Show login screen first
        self.stack.setCurrentWidget(self.login_screen)

        # Example: connect signals to switch pages
        # self.login_screen.login_success.connect(lambda: self.stack.setCurrentWidget(self.main_app_screen))
        # self.main_app_screen.view_vault.connect(lambda: self.stack.setCurrentWidget(self.vault_viewer_screen))
