import orjson
from PySide6 import QtWidgets
from PySide6.QtCore import QObject
from PySide6.QtGui import QSyntaxHighlighter
from PySide6.QtWidgets import QDialog, QGridLayout, QTableWidget, QAbstractItemView, QTableWidgetItem, QTextEdit

import global_objects
from backend.network import Response


class _ResponseBodyWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(global_objects.mono_font)
        self._json: str | None = None

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
        '''split_json = self._json.split("\n")
        for elem, line in enumerate(split_json):
            if "{" in line:
                split_json[elem] = '<p style="color:#adadad">{</p>'

        # convert the split list back into a string
        new_json = ""
        for x in split_json:
            new_json += f"{x}\n"
        self.setText(new_json)'''


class _ResponseHeadersWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        # do some pre-requisites
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(True)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # variables
        headers = ["Key", "Value"]

        # set headers
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # realign headers
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_headers(self, headers: dict):
        """
        Sets a dictionary of headers to the table
        :param headers: Header dictionary
        :return: None
        """
        self.setRowCount(0)
        for header in headers.keys():
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(header))
            self.setItem(row, 1, QTableWidgetItem(headers[header]))


class WindowResponseViewer(QDialog):
    def __init__(self, parent: QObject, response: Response):
        # setup window
        super().__init__(parent)
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self.setMinimumSize(800, 700)
        self.setWindowTitle(f"Response - {response.request_method} - {response.status_code} - {response.request_url}")

        # widgets
        self._response_headers = _ResponseHeadersWidget()
        self._layout.addWidget(self._response_headers)
        self._response_body = _ResponseBodyWidget()
        self._layout.addWidget(self._response_body)

        # variables
        self._response = response

        # exec
        self._populate()

    def _populate(self) -> None:
        """
        Sets the UI state to reflect what is in self._response
        :return: None
        """
        self._response_headers.set_headers(self._response.response_headers)
        self._response_body.set_json(self._response.response_body)

