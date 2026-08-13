from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from model_blame.simir.models import Asset, Quality, Tag, TelemetryBatch, TelemetryKind, TelemetrySample


class TagMappingEntry(BaseModel):
    raw_name: str
    simir_id: str
    asset_id: str
    kind: TelemetryKind
    value_type: str = "json"
    unit: str | None = None
    writable: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_tag(self) -> Tag:
        return Tag(
            tag_id=self.simir_id,
            raw_name=self.raw_name,
            asset_id=self.asset_id,
            kind=self.kind,
            value_type=self.value_type,  # type: ignore[arg-type]
            unit=self.unit,
            writable=self.writable,
            metadata=self.metadata,
        )


class TagMapping(BaseModel):
    backend: str
    scene: str
    assets: list[Asset] = Field(default_factory=list)
    tags: list[TagMappingEntry] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TagMapper:
    def __init__(self, mapping: TagMapping):
        self.mapping = mapping
        self._by_raw = {entry.raw_name: entry for entry in mapping.tags}
        self._by_id = {entry.simir_id: entry for entry in mapping.tags}

    @classmethod
    def from_file(cls, path: str | Path) -> "TagMapper":
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError("PyYAML is required to load SimIR YAML configuration.") from exc

        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return cls(TagMapping.model_validate(data))

    @property
    def raw_names(self) -> list[str]:
        return list(self._by_raw.keys())

    def assets(self) -> list[Asset]:
        if self.mapping.assets:
            return self.mapping.assets
        asset_ids = sorted({entry.asset_id for entry in self.mapping.tags})
        return [Asset(asset_id=asset_id, name=asset_id.replace("_", " ").title(), kind="station") for asset_id in asset_ids]

    def tags(self) -> list[Tag]:
        return [entry.to_tag() for entry in self.mapping.tags]

    def get_by_raw(self, raw_name: str) -> TagMappingEntry:
        return self._by_raw[raw_name]

    def get_by_id(self, tag_id: str) -> TagMappingEntry:
        return self._by_id[tag_id]

    def raw_for_tag_id(self, tag_id: str) -> str:
        return self.get_by_id(tag_id).raw_name

    def sample_for_raw(
        self,
        raw_name: str,
        value: Any,
        run_id: str,
        backend: str,
        sim_time: float | None,
        timestamp: datetime | None = None,
        quality: Quality = Quality.GOOD,
    ) -> TelemetrySample:
        entry = self._by_raw[raw_name]
        value = self._coerce(value, entry.value_type)
        local_name = self._local_name(entry)
        return TelemetrySample(
            timestamp=timestamp or datetime.now().astimezone(),
            sim_time=sim_time,
            run_id=run_id,
            backend=backend,
            asset_id=entry.asset_id,
            tag=local_name,
            kind=entry.kind,
            value=value,
            quality=quality,
            unit=entry.unit,
            metadata={"raw_name": raw_name, **entry.metadata},
        )

    def batch_from_raw(
        self,
        raw_values: dict[str, Any],
        run_id: str,
        backend: str,
        sim_time: float | None,
        timestamp: datetime | None = None,
        include_all: bool = True,
    ) -> TelemetryBatch:
        raw_names = self.raw_names if include_all else [raw_name for raw_name in raw_values if raw_name in self._by_raw]
        samples = [
            self.sample_for_raw(
                raw_name,
                raw_values.get(raw_name),
                run_id,
                backend,
                sim_time,
                timestamp,
                quality=Quality.GOOD if raw_name in raw_values else Quality.MISSING,
            )
            for raw_name in raw_names
        ]
        return TelemetryBatch(run_id=run_id, backend=backend, samples=samples)

    def _local_name(self, entry: TagMappingEntry) -> str:
        prefix = f"{entry.asset_id}."
        if entry.simir_id.startswith(prefix):
            return entry.simir_id[len(prefix) :]
        return entry.simir_id

    def _coerce(self, value: Any, value_type: str) -> Any:
        if value is None:
            return None
        if value_type == "bool":
            if isinstance(value, str):
                return value.lower() in {"1", "true", "yes", "on"}
            return bool(value)
        if value_type == "int":
            return int(value)
        if value_type == "float":
            return float(value)
        if value_type == "str":
            return str(value)
        return value
