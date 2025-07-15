import os
from password_generator import generate_password
from logic import add_password_entry  # <-- Import this!
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QAction, QPixmap, QIcon
from PySide6.QtCore import Qt

class MainAppScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AegisVault - Vault Manager")
        self.setMinimumSize(500, 520)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 40, 50, 40)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Top layout: logo and input section
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        top_layout.setAlignment(Qt.AlignLeft)

        # Logo
        logo_path = os.path.join("assets", "logo.png")
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaledToWidth(80, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("Logo Missing")
            logo_label.setStyleSheet("color: #78A083; font-weight: 600;")
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo_label.setStyleSheet("background-color: transparent;")
        top_layout.addWidget(logo_label)

        # Right side: title + inputs
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        right_layout.setAlignment(Qt.AlignTop)

        title = QLabel("Add New Vault Entry")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 800;
            color: #78A083;
            background-color: transparent;
            margin-bottom: 10px;
        """)
        right_layout.addWidget(title)

        # Helper to add icon to QLineEdit
        def add_icon_to_lineedit(line_edit, icon_path):
            icon = QIcon(icon_path)
            action = QAction(icon, "", line_edit)
            line_edit.addAction(action, QLineEdit.LeadingPosition)

        # Application Name input
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("Application Name")
        self.app_input.setFixedHeight(40)
        self.app_input.setStyleSheet(self.input_style())
        add_icon_to_lineedit(self.app_input, os.path.join("assets", "app.png"))
        right_layout.addWidget(self.app_input)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet(self.input_style())
        add_icon_to_lineedit(self.username_input, os.path.join("assets", "username.png"))
        right_layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet(self.input_style())
        add_icon_to_lineedit(self.password_input, os.path.join("assets", "password.png"))

        # Eye toggle icon action
        self.show_password_action = QAction(QIcon(os.path.join("assets", "eye.png")), "", self.password_input)
        self.show_password_action.setCheckable(True)
        self.show_password_action.toggled.connect(self.toggle_password_visibility)
        self.password_input.addAction(self.show_password_action, QLineEdit.TrailingPosition)

        # Generate password button
        self.generate_password_btn = QPushButton()
        self.generate_password_btn.setIcon(QIcon(os.path.join("assets", "wand.png")))
        self.generate_password_btn.setToolTip("Generate Password")
        self.generate_password_btn.setFixedSize(35, 35)
        self.generate_password_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #78A083;
                border-radius: 5px;
            }
        """)
        self.generate_password_btn.clicked.connect(self.fill_generated_password)

        # Layout for password + generate button
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(6)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.generate_password_btn)
        right_layout.addLayout(password_layout)

        top_layout.addLayout(right_layout)
        main_layout.addLayout(top_layout)

        # Buttons layout (vault dropdown + save button)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.vault_dropdown = QComboBox()
        self.vault_dropdown.setFixedHeight(40)
        self.vault_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #35374B;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                padding: 5px 10px;
                border: 2px solid #78A083;
                min-width: 120px;
            }
            QComboBox:hover {
                background-color: #50727B;
                border: 2px solid #344955;
            }
            QComboBox QAbstractItemView {
                background-color: #344955;
                color: white;
                selection-background-color: #78A083;
            }
        """)

        # Add vaults with icons
        self.vault_dropdown.addItem(QIcon(os.path.join("assets", "personal.png")), "Personal")
        self.vault_dropdown.addItem(QIcon(os.path.join("assets", "work.png")), "Work")
        self.vault_dropdown.addItem(QIcon(os.path.join("assets", "bank.png")), "Bank")
        self.vault_dropdown.addItem(QIcon(os.path.join("assets", "ghost.png")), "Ghost")

        btn_layout.addWidget(self.vault_dropdown)

        self.save_btn = QPushButton("Save Entry")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #50727B;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
                border: 2px solid #78A083;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #78A083;
                border: 2px solid #50727B;
                color: #344955;
            }
            QPushButton:pressed {
                background-color: #609376;
            }
        """)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

        # Vaults button with icon
        self.vaults_btn = QPushButton("Vaults")
        self.vaults_btn.setFixedHeight(45)
        self.vaults_btn.setIcon(QIcon(os.path.join("assets", "vault.png")))
        self.vaults_btn.setStyleSheet("""
            QPushButton {
                background-color: #50727B;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
                border: 2px solid #78A083;
                margin-top: 20px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #78A083;
                border: 2px solid #50727B;
                color: #344955;
            }
            QPushButton:pressed {
                background-color: #609376;
            }
        """)
        self.vaults_btn.setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.vaults_btn, alignment=Qt.AlignCenter)

        # Logout button without icon (icon not found in assets)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setFixedHeight(50)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #35374B;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                border: 2px solid #78A083;
                margin-top: 15px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #50727B;
                border: 2px solid #344955;
                color: white;
            }
            QPushButton:pressed {
                background-color: #609376;
            }
        """)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.logout_btn, alignment=Qt.AlignCenter)

        # Set background color for the whole widget (optional if using QSS)
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #6096B4;
        #         color: white;
        #     }
        # """)

        # Connect signals
        self.save_btn.clicked.connect(self.save_entry)
        self.logout_btn.clicked.connect(self.logout)
        self.vaults_btn.clicked.connect(self.go_to_vaults_page)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_action.setIcon(QIcon(os.path.join("assets", "eye_slash.png")))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_action.setIcon(QIcon(os.path.join("assets", "eye.png")))

    def input_style(self):
        return """
            background-color: #344955;
            color: white;
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 16px;
            border: 2px solid #50727B;
            selection-background-color: #78A083;
        """

    def fill_generated_password(self):
        new_password = generate_password()
        self.password_input.setText(new_password)

    def save_entry(self):
        app = self.app_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        vault = self.vault_dropdown.currentText()

        if not app or not username or not password:
            QMessageBox.warning(self, "Incomplete Data", "Please fill all fields.")
            return

        # Actually save the entry!
        add_password_entry(app, username, password, vault)

        QMessageBox.information(
            self,
            "Entry Saved",
            f"Saved entry to '{vault}' vault:\nApp: {app}\nUsername: {username}"
        )
        self.app_input.clear()
        self.username_input.clear()
        self.password_input.clear()

    def logout(self):
        if self.parent() and hasattr(self.parent(), "show_login_screen"):
            self.parent().show_login_screen()

    def go_to_vaults_page(self):
        if self.parent() and hasattr(self.parent(), "show_vaults_screen"):
            self.parent().show_vaults_screen()