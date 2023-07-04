from copy import deepcopy
from dataclasses import dataclass
from urllib.parse import urlencode

from PySide6.QtCore import QObject, Signal, QByteArray
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from orjson import orjson

import global_objects


@dataclass
class Response:
    status_code: int
    response_body: dict | list | str
    response_headers: dict


class Request(QObject):
    response = Signal(Response)
    error = Signal(str)

    def __init__(self, parent: QObject):
        super().__init__(parent)

        # variables
        self._qt_reply: QNetworkReply | None = None

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
                appended_url += f"?{urlencode(x)}={urlencode(query_params[x])}"

        # build the qt network request object
        qt_request = QNetworkRequest(appended_url)
        if type(headers) is dict:
            for x in headers.keys():
                qt_request.setHeader(x, headers[x])

        # send the request (we cant use named parameters here... why?)
        self._qt_reply = global_objects.nam.sendCustomRequest(
            qt_request,
            method.encode(),
            orjson.dumps(body),
        )
        self._qt_reply.errorOccurred.connect(self._emit_error)
        self._qt_reply.readyRead.connect(self._build_emit_response)

    def _emit_error(self) -> None:
        print("error")

    def _build_emit_response(self) -> None:
        """
        Called when self._qt_reply is ready to read, puts the response into a Response object and emits it as the
        `response` signal
        :return: None
        """
        # try to parse the response payload as JSON
        try:
            parsed_payload = orjson.loads(self._qt_reply.readAll().data())
        except orjson.JSONDecodeError as e:
            self.error.emit("Response is not parsable JSON")
            return

        # parse the response headers
        parsed_headers = {}
        for x in self._qt_reply.rawHeaderPairs():
            x: tuple[QByteArray, QByteArray]
            parsed_headers[x[0].toStdString()] = x[1].toStdString()

        # build and emit the response object
        response = Response(
            status_code=self._qt_reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute),
            response_body=parsed_payload,
            response_headers=parsed_headers
        )
        self.response.emit(response)