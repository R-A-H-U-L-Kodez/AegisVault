import hashlib
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from logic import totp_verify  # Your TOTP verification function

def show_invalid_message(self):
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.warning(self, "Error", "Invalid TOTP code. Please try again.")
    self.totp_input.clear()
    self.totp_input.setFocus()
class TotpScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AegisVault - TOTP Verification")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Title label
        title = QLabel("Enter 6-Digit TOTP Code")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 700;
            color: #78A083;
            margin-bottom: 25px;
            letter-spacing: 1.1px;
            background-color: transparent;
        """)
        layout.addWidget(title)

        # TOTP input
        self.totp_input = QLineEdit()
        self.totp_input.setPlaceholderText("123456")
        self.totp_input.setMaxLength(6)
        self.totp_input.setFixedHeight(45)
        self.totp_input.setAlignment(Qt.AlignCenter)
        self.totp_input.setStyleSheet("""
            background-color: #344955;
            color: white;
            font-size: 20px;
            border-radius: 10px;
            border: 2px solid #50727B;
            letter-spacing: 10px;
        """)
        layout.addWidget(self.totp_input)

        # Verify button
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setFixedHeight(45)
        self.verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #35374B;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
                border: 2px solid #78A083;
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
        self.verify_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.verify_btn)

        # Footer text
        footer = QLabel("Secure two-factor authentication")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            color: #78A083;
            font-size: 13px;
            font-style: italic;
            margin-top: 30px;
            letter-spacing: 0.5px;
            background-color: transparent;
        """)
        layout.addWidget(footer)

        # Background color for widget
        self.setStyleSheet("""
            QWidget {
                background-color: #344955;
                color: white;
            }
        """)

        # Connect signals
        self.verify_btn.clicked.connect(self.check_totp)
        self.totp_input.returnPressed.connect(self.verify_btn.click)

        # Auto-focus the input field shortly after show
        QTimer.singleShot(100, self.totp_input.setFocus)

    def check_totp(self):
        entered_code = self.totp_input.text().strip()
        if totp_verify(entered_code):
            QMessageBox.information(self, "Success", "TOTP verified! Access granted.")
            if self.parent() and hasattr(self.parent(), "show_main_screen"):
                self.parent().show_main_screen()
        else:
            QMessageBox.warning(self, "Error", "Invalid TOTP code. Please try again.")
            self.totp_input.clear()
            self.totp_input.setFocus()
