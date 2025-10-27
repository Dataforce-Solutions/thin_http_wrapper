import typing
from typing import Any

import httpx

from .types import HTTPError, Response


class HTTPClient:
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_redirects: int = 10,
        verify: bool = True,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        proxy: str | None = None,
        default_encoding: str | typing.Callable[[bytes], str] = "utf-8",
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            follow_redirects=True,
            max_redirects=max_redirects,
            verify=verify,
            headers=headers,
            cookies=cookies,
            proxy=proxy,
            default_encoding=default_encoding,
        )

    def _execute_request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
            )
            response.raise_for_status()
            return Response(response)
        except httpx.HTTPStatusError as error:
            raise HTTPError(
                message=str(error),
                status_code=error.response.status_code,
                response=Response(error.response),
            ) from error
        except httpx.RequestError as error:
            raise HTTPError(message=f"Request failed: {error}") from error

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._execute_request("GET", url, params=params, headers=headers)

    def post(
        self,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._execute_request("POST", url, data=data, json=json, headers=headers)

    def put(
        self,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._execute_request("PUT", url, data=data, json=json, headers=headers)

    def patch(
        self,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._execute_request(
            "PATCH", url, data=data, json=json, headers=headers
        )

    def delete(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._execute_request("DELETE", url, headers=headers)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._execute_request(
            method, url, params=params, data=data, json=json, headers=headers
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, *args: Any) -> None:  # noqa ANN401
        self.close()
