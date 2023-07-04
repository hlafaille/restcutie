from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QMenuBar, QGroupBox, QGridLayout, QWidget, QTabWidget, QTableWidget, \
    QPushButton, QAbstractItemView, QComboBox, QSizePolicy, QLineEdit

import global_objects
from backend.network import Request, Response
from ui.custom_widgets import LineEditWithLabel
from ui.response_viewer import WindowResponseViewer


class WindowHome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rest, Cutie - A fast REST client written in Qt")
        self.setMinimumSize(1200, 800)

        self._widget = QWidget()
        self._layout = QGridLayout(self._widget)
        self.setCentralWidget(self._widget)

        # do menu bar
        self._menu_bar = QMenuBar(self)
        self._file_menu = self._menu_bar.addMenu("File")
        self._file_menu = self._menu_bar.addMenu("Edit")
        self.setMenuBar(self._menu_bar)

        self._assemble_request = AssembleRequestWidget()
        self._layout.addWidget(self._assemble_request)


class _EditRequestBodyWidget(QTableWidget):
    """Widget for editing the request body"""
    def __init__(self):
        super().__init__()


class _EditQueryParametersWidget(QWidget):
    """Widget for editing headers"""
    class _Table(QTableWidget):
        def __init__(self):
            super().__init__()
            # do some pre-requisites
            self.verticalHeader().setVisible(False)
            self.setSortingEnabled(True)
            self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

            # variables
            headers = ["Key", "Value"]

            # set headers
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)

            # realign headers
            self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def __init__(self):
        super().__init__()
        self._layout = QGridLayout()
        self.setLayout(self._layout)

        self.add_button = QPushButton("Add")
        self.add_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._layout.addWidget(self.add_button, 0, 0)
        self.remove_button = QPushButton("Remove")
        self.remove_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._layout.addWidget(self.remove_button, 0, 1)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self._layout.addWidget(self.search, 0, 2)
        self.table = self._Table()
        self._layout.addWidget(self.table, 1, 0, 1, 3)


class _EditHeadersWidget(QWidget):
    """Widget for editing headers"""
    class _Table(QTableWidget):
        def __init__(self):
            super().__init__()
            # do some pre-requisites
            self.verticalHeader().setVisible(False)
            self.setSortingEnabled(True)
            self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

            # variables
            headers = ["Key", "Value"]

            # set headers
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)

            # realign headers
            self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def __init__(self):
        super().__init__()
        self._layout = QGridLayout()
        self.setLayout(self._layout)

        self.add_button = QPushButton("Add")
        self.add_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._layout.addWidget(self.add_button, 0, 0)
        self.remove_button = QPushButton("Remove")
        self.remove_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._layout.addWidget(self.remove_button, 0, 1)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self._layout.addWidget(self.search, 0, 2)
        self.table = self._Table()
        self._layout.addWidget(self.table, 1, 0, 1, 3)


class _RequestAttributesWidget(QTabWidget):
    """Widget for modifying the attributes of a request"""
    def __init__(self):
        super().__init__()
        self.headers_editor = _EditHeadersWidget()
        self.addTab(self.headers_editor, "Headers")
        self.query_parameters = _EditQueryParametersWidget()
        self.addTab(self.query_parameters, "Query Parameters")
        self.request_body = _EditRequestBodyWidget()
        self.addTab(self.request_body, "Body")


class AssembleRequestWidget(QGroupBox):
    """Widget for creating a request"""
    def __init__(self):
        super().__init__(title="Request")
        self._layout = QGridLayout()
        self.setLayout(self._layout)

        # base url input box
        self.base_url = LineEditWithLabel(self, label="Base URL", placeholder="https://api.mysite.com")
        self.base_url.line_edit.setFont(global_objects.mono_font)
        self._layout.addWidget(self.base_url, 0, 0)

        # path to resource input box
        self.path = LineEditWithLabel(self, label="Path", placeholder="/path/to/resource")
        self.path.line_edit.setFont(global_objects.mono_font)
        self._layout.addWidget(self.path, 0, 1)

        # tab widget
        self._request_attributes = _RequestAttributesWidget()
        self._layout.addWidget(self._request_attributes, 1, 0, 1, 2)

        self.method = QComboBox()
        self.method.addItems(["GET", "POST", "PUT", "DELETE", "PATCH"])
        self._layout.addWidget(self.method, 2, 0, 2, 1)

        # submit button
        self.send_request_button = QPushButton("Send Request")
        self.send_request_button.clicked.connect(self.send_request)
        self._layout.addWidget(self.send_request_button, 2, 1, 2, 2)

    def _process_response(self, response: Response):
        """
        Processes the response from the provided HTTP request
        :param response:
        :return:
        """
        response_viewer = WindowResponseViewer(self, response)
        response_viewer.exec()

    def send_request(self):
        """
        Called when self.send_request_button is clicked, sends the built request
        :return:
        """
        request = Request(self)
        request.response.connect(self._process_response)
        request.custom(
            method=self.method.currentText(),
            url=self.base_url + self.path,
            query_params=None,
            headers=None,
            body=None
        )