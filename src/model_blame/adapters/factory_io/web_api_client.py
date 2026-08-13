from __future__ import annotations

from typing import Any


class FactoryIOWebApiClient:
    """Small live integration scaffold for a Factory I/O Web API transport.

    Factory I/O deployments differ in driver/API setup, so endpoint names are
    intentionally injected through configuration instead of hard-coded here.
    """

    def __init__(self, host: str, port: int, endpoints: dict[str, str | None] | None = None):
        self.host = host
        self.port = port
        self.endpoints = endpoints or {}
        self.base_url = f"http://{host}:{port}"
        self._client = None

    def connect(self) -> None:
        try:
            import httpx
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install the factoryio-web extra to use the Factory I/O Web API transport.") from exc
        self._client = httpx.Client(base_url=self.base_url, timeout=5.0)

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None

    def health(self) -> dict[str, Any]:
        return {"connected": self._client is not None, "base_url": self.base_url}

    def read_tags(self, raw_names: list[str]) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("Factory I/O Web API client is not connected.")
        endpoint = self.endpoints.get("read_tags")
        if not endpoint:
            raise NotImplementedError("Configure endpoints.read_tags for this Factory I/O Web API setup.")
        response = self._client.post(endpoint, json={"tags": raw_names})
        response.raise_for_status()
        data = response.json()
        return data.get("tags", data)

    def write_tag(self, raw_name: str, value: Any) -> None:
        if self._client is None:
            raise RuntimeError("Factory I/O Web API client is not connected.")
        endpoint = self.endpoints.get("write_tag")
        if not endpoint:
            raise NotImplementedError("Configure endpoints.write_tag for this Factory I/O Web API setup.")
        response = self._client.post(endpoint, json={"tag": raw_name, "value": value})
        response.raise_for_status()

    def reset(self) -> None:
        if self._client is None:
            raise RuntimeError("Factory I/O Web API client is not connected.")
        endpoint = self.endpoints.get("reset")
        if not endpoint:
            raise NotImplementedError("Configure endpoints.reset for this Factory I/O Web API setup.")
        response = self._client.post(endpoint)
        response.raise_for_status()
