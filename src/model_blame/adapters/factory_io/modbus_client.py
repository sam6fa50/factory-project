from __future__ import annotations


class FactoryIOModbusClient:
    def __init__(self, host: str, port: int, unit_id: int = 1):
        self.host = host
        self.port = port
        self.unit_id = unit_id

    def connect(self) -> None:
        raise NotImplementedError("Modbus TCP transport is scaffolded; wire pymodbus register reads here.")

    def disconnect(self) -> None:
        return None
