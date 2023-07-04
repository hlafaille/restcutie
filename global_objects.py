from PySide6.QtGui import QFont
from PySide6.QtNetwork import QNetworkAccessManager
from PySide6.QtWidgets import QApplication

app: QApplication | None = None
mono_font_id: int | None = None
mono_font: QFont | None = None
nam = QNetworkAccessManager(app)
