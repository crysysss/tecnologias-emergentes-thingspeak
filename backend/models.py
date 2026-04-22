from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TelemetrySource = Literal["live", "fixture"]
TelemetryChannelState = Literal["live_data", "live_empty", "fixture_fallback", "fixture_only"]
TelemetryHeuristicState = Literal["stable", "warning", "critical"]


class ChannelFieldDefinition(BaseModel):
    key: str
    label: str
    unit: str
    description: str
    min_value: float
    max_value: float | None = None


class ChannelInfo(BaseModel):
    channel_id: int
    name: str
    author: str
    access: str
    description: str
    fields: list[ChannelFieldDefinition]
    live_reads_enabled: bool
    writes_enabled: bool
    read_source_mode: str


class TelemetryMeasurement(BaseModel):
    entry_id: int
    recorded_at: datetime
    source: TelemetrySource
    cognitive_load_pct: float = Field(..., ge=0, le=100)
    coherence_level_pct: float = Field(..., ge=0, le=100)
    emotional_intensity_pct: float = Field(..., ge=0, le=100)
    inference_latency_ms: float = Field(..., ge=0)
    power_consumption_w: float = Field(..., ge=0)
    stability_state: TelemetryHeuristicState
    diagnostic_flags: list[str]
    warnings: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app_name: str
    source: str
    detail: str
    live_reads_enabled: bool
    writes_enabled: bool
    fallback_samples: int
    channel_id: int


class HistoryResponse(BaseModel):
    source: TelemetrySource
    channel_state: TelemetryChannelState
    count: int
    detail: str
    fallback_reason: str | None = None
    measurements: list[TelemetryMeasurement]


class LatestResponse(BaseModel):
    source: TelemetrySource
    channel_state: TelemetryChannelState
    detail: str
    fallback_reason: str | None = None
    measurement: TelemetryMeasurement | None


class TelemetryPreviewRequest(BaseModel):
    cognitive_load_pct: float
    coherence_level_pct: float
    emotional_intensity_pct: float
    inference_latency_ms: float
    power_consumption_w: float


class TelemetryPreviewResponse(BaseModel):
    mode: Literal["preview_only"]
    writes_enabled: bool
    payload: dict[str, str]
    request_template: str
    warnings: list[str]
    heuristic_state: TelemetryHeuristicState
    detail: str


class TelemetryWriteRequest(TelemetryPreviewRequest):
    pass


class TelemetryWriteResponse(BaseModel):
    mode: Literal["live_write"]
    writes_enabled: bool
    channel_id: int
    entry_id: int
    payload: dict[str, str]
    request_template: str
    warnings: list[str]
    heuristic_state: TelemetryHeuristicState
    detail: str
