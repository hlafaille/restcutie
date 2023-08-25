from copy import deepcopy
from dataclasses import dataclass
from urllib.parse import urlencode, quote

from PySide6.QtCore import QObject, Signal, QByteArray
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from orjson import orjson

import global_objects


@dataclass
class Response:
    status_code: int
    response_body: dict | list | str
    response_headers: dict
    request_url: str
    request_method: str


class WrappedQNetworkReply(QObject):
    def __init__(self, network_reply: QNetworkReply, method: str):
        super().__init__()
        self.method = method
        self.network_reply = network_reply


class Request(QObject):
    response = Signal(Response)
    error = Signal()

    def __init__(self, parent: QObject):
        super().__init__(parent)

        # variables
        self._qt_reply: WrappedQNetworkReply | None = None

    def custom(self, method: str, url: str, query_params: dict | None, headers: dict | None, body: dict | list | str | None):
        """
        Send a custom request
        :param method: HTTP Method
        :param url: URL receiving the request
        :param query_params: Optional, Query parameters
        :param headers: Optional, HTTP Headers
        :param body: Optional, Request body
        :return: None
        """
        # iterate over the query params, append them to our url
        appended_url = deepcopy(url)
        if type(query_params) is dict:
            for x in query_params.keys():
                appended_url += f"?{quote(x)}={quote(query_params[x])}"

        # build the qt network request object
        qt_request = QNetworkRequest(appended_url)
        if type(headers) is dict:
            for x in headers.keys():
                qt_request.setHeader(x, headers[x])

        # send the request (we cant use named parameters here... why?)
        qt_reply = global_objects.nam.sendCustomRequest(
            qt_request,
            method.encode(),
            orjson.dumps(body),
        )
        qt_reply.errorOccurred.connect(self._emit_error)
        qt_reply.readyRead.connect(self._build_emit_response)
        self._qt_reply = WrappedQNetworkReply(qt_reply, method)

    def _emit_error(self) -> None:
        self.error.emit()

    def _build_emit_response(self) -> None:
        """
        Called when self._qt_reply is ready to read, puts the response into a Response object and emits it as the
        `response` signal
        :return: None
        """
        # try to parse the response payload as JSON
        try:
            parsed_payload = orjson.loads(self._qt_reply.network_reply.readAll().data())
        except orjson.JSONDecodeError as e:
            self.error.emit()
            return

        # parse the response headers
        parsed_headers = {}
        for x in self._qt_reply.network_reply.rawHeaderPairs():
            x: tuple[QByteArray, QByteArray]
            parsed_headers[x[0].toStdString()] = x[1].toStdString()

        # build and emit the response object
        response = Response(
            status_code=self._qt_reply.network_reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute),
            response_body=parsed_payload,
            response_headers=parsed_headers,
            request_url=self._qt_reply.network_reply.url().toString(),
            request_method=self._qt_reply.method
        )
        self.response.emit(response)