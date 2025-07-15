import os
import hashlib
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect, QFrame
)

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPixmap, QColor
from totp_screen import TotpScreen

class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AegisVault - Login")
        self.setMinimumSize(600, 400)
        self.setObjectName("LoginScreen")

        # Outer layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        # Card container with dark background
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(400)
        card.setStyleSheet("""
            QFrame#loginCard {
                background: #23242A;
                border-radius: 18px;
                padding: 32px 32px 24px 32px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Logo
        logo_path = os.path.join("assets", "logo.png")
        logo_label = QLabel()
        logo_label.setObjectName("logoLabel")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(16)
            shadow.setOffset(0, 3)
            shadow.setColor(QColor("#6096B4"))
            logo_label.setGraphicsEffect(shadow)
        else:
            logo_label.setText("AegisVault\nLogo Missing")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("background: transparent; color: #6096B4; font-weight: bold;")
        layout.addWidget(logo_label)

        # Title
        title = QLabel("Welcome to AegisVault")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #78A083;
            letter-spacing: 1px;
            background: transparent;
        """)
        layout.addWidget(title)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: #344955;
                border: 2px solid #78A083;
                border-radius: 10px;
                font-size: 16px;
                padding: 8px 12px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6096B4;
                background: #23242A;
            }
        """)
        layout.addWidget(self.password_input)

        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedHeight(44)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6096B4, stop:1 #78A083);
                color: white;
                border-radius: 10px;
                font-size: 17px;
                font-weight: 700;
                border: none;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: #50727B;
                color: #fff;
            }
        """)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.login_btn)

        # Message label
        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setStyleSheet("font-size: 15px; font-weight: 500; min-height: 20px; color: #FF6666;")
        self.msg_label.setVisible(False)
        layout.addWidget(self.msg_label)

        # Footer
        footer = QLabel("Secured with AES-256 encryption & TOTP 2FA")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 12px; color: #A5C9CA; margin-top: 10px; background: transparent;")
        layout.addWidget(footer)

        outer_layout.addWidget(card, alignment=Qt.AlignCenter)

        # Password hash for "1" (for demonstration)
        self.correct_password_hash = hashlib.sha256("1".encode()).hexdigest()

        # Connect signals
        self.login_btn.clicked.connect(self.check_password)
        self.password_input.returnPressed.connect(self.login_btn.click)

        # Load custom theme if available
        if os.path.exists("theme.qss"):
            with open("theme.qss", "r") as f:
                self.setStyleSheet(f.read())

    def check_password(self):
        entered_pwd = self.password_input.text()
        entered_hash = hashlib.sha256(entered_pwd.encode()).hexdigest()

        def show_message(msg, color):
            self.msg_label.setText(msg)
            self.msg_label.setStyleSheet(
                f"font-size: 15px; font-weight: 500; color: {color}; min-height: 20px;"
            )
            self.msg_label.setVisible(True)
            animation = QPropertyAnimation(self.msg_label, b"windowOpacity")
            animation.setDuration(500)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start(QPropertyAnimation.DeleteWhenStopped)

        if entered_hash == self.correct_password_hash:
            
            QTimer.singleShot(800, self.show_totp_screen)  # Add a short delay for UX
        else:
            show_message("Incorrect Master Password.", "#FF6666")
            self.password_input.clear()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = LoginScreen()
    win.show()
    sys.exit(app.exec())

