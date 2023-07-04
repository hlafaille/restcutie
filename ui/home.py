import os.path

import orjson
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QMenuBar, QGroupBox, QGridLayout, QWidget, QTabWidget, QTableWidget, \
    QPushButton, QAbstractItemView, QComboBox, QSizePolicy, QLineEdit, QTableWidgetItem, QTextEdit, QFileDialog

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

        # build menu bar
        self._menu_bar = QMenuBar(self)
        self._file_menu = self._menu_bar.addMenu("File")
        file_open = self._file_menu.addAction("Open")
        file_open.triggered.connect(self.open_session)
        file_save = self._file_menu.addAction("Save")
        file_save.triggered.connect(self.save_session)

        self._edit_menu = self._menu_bar.addMenu("Edit")
        edit_variables = self._edit_menu.addAction("Variables")
        self._edit_menu.addSeparator()
        self.setMenuBar(self._menu_bar)

        self._assemble_request = AssembleRequestWidget()
        self._layout.addWidget(self._assemble_request)

    def open_session(self):
        """
        Open a session from a file
        :return:
        """
        def _open(path: str):
            print(path)
        file = QFileDialog(self, "Open Session", os.path.expanduser("~"), ".sesh")
        file.fileSelected.connect(_open)
        file.exec()

    def save_session(self):
        """
        Write the session to a file
        :return: None
        """
        def _save(path: str):
            print(path)
        file = QFileDialog(self, "Save Session", os.path.expanduser("~"), ".sesh")
        file.fileSelected.connect(_save)
        file.exec()


class _EditRequestBodyWidget(QWidget):
    """Widget for editing the request body"""
    class _Editor(QTextEdit):
        def __init__(self):
            super().__init__()
            self.setFont(global_objects.mono_font)
            self._json: str | None = None

        def prettify_json(self):
            """
            Prettifies the JSON
            :return: None
            """
            try:
                self._json = self.toPlainText()
                parsed_json = orjson.loads(self._json)
                self._json = orjson.dumps(parsed_json, option=orjson.OPT_INDENT_2).decode()
                self.setText(self._json)
            except orjson.JSONDecodeError:
                pass

        def set_json(self, json_: str):
            self._json = orjson.dumps(json_, option=orjson.OPT_INDENT_2).decode()
            self._highlight_syntax()

        def _highlight_syntax(self):
            """
            Iterates over the lines in the JSON, applying HTML syntax highlighting
            todo needs work
            :return: None
            """
            self.setText(self._json)

    def __init__(self):
        super().__init__()
        self._layout = QGridLayout()
        self.setLayout(self._layout)

        self.editor = self._Editor()
        self._layout.addWidget(self.editor, 1, 0)
        self.prettify_button = QPushButton("Prettify")
        self.prettify_button.clicked.connect(self.editor.prettify_json)
        self._layout.addWidget(self.prettify_button, 0, 0)

    def get(self) -> dict:
        """
        Gets the content of Editor as a dictionary
        :return: Dictionary
        """
        try:
            return orjson.loads(self.editor.toPlainText())
        except orjson.JSONDecodeError:
            return {}


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
        self.add_button.clicked.connect(self.add_new)
        self._layout.addWidget(self.add_button, 0, 0)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.remove_button.clicked.connect(self.remove)
        self._layout.addWidget(self.remove_button, 0, 1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self._layout.addWidget(self.search, 0, 2)

        self.table = self._Table()
        self._layout.addWidget(self.table, 1, 0, 1, 3)

    def add(self, key: str, value: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(key))
        self.table.setItem(row, 1, QTableWidgetItem(value))

    def add_new(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QTableWidgetItem()
        self.table.setItem(row, 0, item)
        self.table.editItem(item)

    def remove(self):
        row = self.table.currentRow()
        self.table.removeRow(row)

    def get(self) -> dict:
        """
        Get this table as a key/value pair
        :return: None
        """
        content = {}
        for row in range(self.table.rowCount()):
            key = self.table.item(row, 0).text()
            value = self.table.item(row, 1).text()
            content[key] = value
        return content


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
        self.add_button.clicked.connect(self.add_new)
        self._layout.addWidget(self.add_button, 0, 0)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.remove_button.clicked.connect(self.remove)
        self._layout.addWidget(self.remove_button, 0, 1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self._layout.addWidget(self.search, 0, 2)

        self.table = self._Table()
        self._layout.addWidget(self.table, 1, 0, 1, 3)

    def add(self, key: str, value: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(key))
        self.table.setItem(row, 1, QTableWidgetItem(value))

    def add_new(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QTableWidgetItem()
        self.table.setItem(row, 0, item)
        self.table.editItem(item)

    def remove(self):
        row = self.table.currentRow()
        self.table.removeRow(row)

    def get(self) -> dict:
        """
        Get this table as a key/value pair
        :return: None
        """
        content = {}
        for row in range(self.table.rowCount()):
            key = self.table.item(row, 0).text()
            value = self.table.item(row, 1).text()
            content[key] = value
        return content


class _RequestAttributesWidget(QTabWidget):
    """Widget for modifying the attributes of a request"""
    def __init__(self):
        super().__init__()
        self.headers_editor = _EditHeadersWidget()
        self.addTab(self.headers_editor, "Headers")
        self.query_parameters_editor = _EditQueryParametersWidget()
        self.addTab(self.query_parameters_editor, "Query Parameters")
        self.request_body_editor = _EditRequestBodyWidget()
        self.addTab(self.request_body_editor, "Body")


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
            query_params=self._request_attributes.query_parameters_editor.get(),
            headers=self._request_attributes.headers_editor.get(),
            body=self._request_attributes.request_body_editor.get()
        )