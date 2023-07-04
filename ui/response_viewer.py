import orjson
from PySide6 import QtWidgets
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QGridLayout, QTableWidget, QAbstractItemView, QTableWidgetItem, QTextEdit

from backend.network import Response


class _ResponseBodyWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def set_json(self, json_: str):
        self.setText(orjson.dumps(json_, option=orjson.OPT_INDENT_2).decode())
        self._highlight_syntax()

    def _highlight_syntax(self):
        pass


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

