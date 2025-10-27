import json as jsonlib
import typing
from dataclasses import dataclass

import httpx


class Response:
    def __init__(self, httpx_response: httpx.Response) -> None:
        self._httpx_response = httpx_response
        self.status_code = self._httpx_response.status_code
        self.headers = dict(self._httpx_response.headers)
        self.content = self._httpx_response.content
        self.text = self._httpx_response.text
        self.url = str(self._httpx_response.url)
        self.encoding = self._httpx_response.encoding

    def json(self, **kwargs) -> typing.Any:  # noqa ANN401
        return jsonlib.loads(self.content, **kwargs)

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        return 400 <= self.status_code < 600

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.status_code < 400

    def raise_for_status(self) -> None:
        if not self.is_success:
            status_class = self.status_code // 100
            error_types = {
                1: "Informational response",
                3: "Redirect response",
                4: "Client error",
                5: "Server error",
            }
            raise HTTPError(
                message=error_types.get(status_class, "HTTP Error"),
                status_code=self.status_code,
                response=self,
            )


@dataclass
class HTTPError(Exception):
    def __init__(
        self,
        *,
        message: str,
        status_code: int | None = None,
        response: Response | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code or (response.status_code if response else None)
        self.response = response

    def __str__(self) -> str:
        if self.status_code:
            return f"HTTP {self.status_code}: {self.message}"
        return self.message
