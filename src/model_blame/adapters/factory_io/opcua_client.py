from __future__ import annotations


class FactoryIOOpcUaClient:
    def __init__(self, host: str, port: int, namespace: str | None = None):
        self.host = host
        self.port = port
        self.namespace = namespace

    def connect(self) -> None:
        raise NotImplementedError("OPC UA transport is scaffolded; wire asyncua tag reads here.")

    def disconnect(self) -> None:
        return None
