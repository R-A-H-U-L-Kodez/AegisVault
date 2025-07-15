from PySide6.QtWidgets import QLineEdit, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

def add_icon_to_lineedit(line_edit: QLineEdit, icon_path: str):
    """Adds an icon to the left side of a QLineEdit (inside the field)."""
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