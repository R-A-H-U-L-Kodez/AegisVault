import sys
from PySide6.QtWidgets import QApplication, QStackedWidget
from login_screen import LoginScreen
from totp_screen import TotpScreen
from main_app_screen import MainAppScreen
from vault_viewer import VaultViewerScreen


class AegisVaultApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Screens
        self.login_screen = LoginScreen(self)
        self.totp_screen = TotpScreen(self)
        self.main_screen = MainAppScreen(self)
        self.vault_viewer_screen = VaultViewerScreen(self)

        # Add screens to stack
        self.addWidget(self.login_screen)
        self.addWidget(self.totp_screen)
        self.addWidget(self.main_screen)
        self.addWidget(self.vault_viewer_screen)

        # Start with Login Screen
        self.setCurrentWidget(self.login_screen)

        # Button connections
        self.login_screen.login_btn.clicked.connect(self.show_totp_screen)
        self.totp_screen.verify_btn.clicked.connect(self.verify_totp)

        self.main_screen.logout_btn.clicked.connect(self.show_login_screen)
        self.main_screen.vaults_btn.clicked.connect(self.show_vaults_screen)

        self.vault_viewer_screen.close_btn.clicked.connect(self.show_main_screen)

    def show_login_screen(self):
        self.login_screen.password_input.clear()
        self.setCurrentWidget(self.login_screen)

    def show_totp_screen(self):
        self.totp_screen.totp_input.clear()
        self.setCurrentWidget(self.totp_screen)

    def verify_totp(self):
        entered_code = self.totp_screen.totp_input.text().strip()
        if entered_code == "123456":  # Replace with real TOTP logic
            self.show_main_screen()
        else:
            self.totp_screen.show_invalid_message()

    def show_main_screen(self):
        self.main_screen.app_input.clear()
        self.main_screen.username_input.clear()
        self.main_screen.password_input.clear()
        self.setCurrentWidget(self.main_screen)

    def show_vaults_screen(self):
        self.vault_viewer_screen.load_vault_entries()
        self.setCurrentWidget(self.vault_viewer_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AegisVaultApp()
    window.setWindowTitle("AegisVault")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
