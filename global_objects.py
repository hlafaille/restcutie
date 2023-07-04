from PySide6.QtNetwork import QNetworkAccessManager
from PySide6.QtWidgets import QApplication

app: QApplication | None = None
nam = QNetworkAccessManager(app)
