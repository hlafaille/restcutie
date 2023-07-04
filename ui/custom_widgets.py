from PySide6.QtCore import QObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QSizePolicy


class LineEditWithLabel(QWidget):
    def __init__(self, parent: QObject, label: str, placeholder: str | None = None, monospace: bool = False):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.label = QLabel(label)
        self._layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        if monospace:
            self.line_edit.setFont(QFont(""))
        if placeholder:
            self.line_edit.setPlaceholderText(placeholder)
        self._layout.addWidget(self.line_edit)

    def __str__(self) -> str:
        return self.line_edit.text()

    def __add__(self, x):
        return str(self) + str(x)