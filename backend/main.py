from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.config import load_settings
from backend.models import (
    ChannelInfo,
    HealthResponse,
    HistoryResponse,
    LatestResponse,
    TelemetryPreviewRequest,
    TelemetryPreviewResponse,
    TelemetryWriteRequest,
    TelemetryWriteResponse,
)
from backend.service import ControlledReadRejected, ControlledWriteRejected, TelemetryService
from backend.thingspeak_client import ThingSpeakUnavailable


settings = load_settings()

app = FastAPI(
    title="NeuroBotics Telemetry API",
    version="0.1.0",
    summary="API segura para lectura del canal publico y previsualizacion de escrituras.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://127.0.0.1:4321",
        "http://localhost:4321",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_service() -> TelemetryService:
    # Se instancia por request para que cada llamada lea la configuracion actual
    # cacheada y no arrastre estado mutable entre pruebas o ejecuciones.
    return TelemetryService()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "NeuroBotics Telemetry API",
        "mode": "safe-preview",
        "docs": "/docs",
    }


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return get_service().get_health()


@app.get("/api/channel", response_model=ChannelInfo)
def channel() -> ChannelInfo:
    return get_service().get_channel_info()


@app.get("/api/telemetry/history", response_model=HistoryResponse)
def telemetry_history(limit: int = Query(default=10, ge=1, le=50)) -> HistoryResponse:
    try:
        return get_service().get_history(limit=limit)
    except ControlledReadRejected as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ThingSpeakUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/telemetry/latest", response_model=LatestResponse)
def telemetry_latest() -> LatestResponse:
    try:
        return get_service().get_latest()
    except ControlledReadRejected as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ThingSpeakUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/telemetry/preview", response_model=TelemetryPreviewResponse)
def telemetry_preview(request: TelemetryPreviewRequest) -> TelemetryPreviewResponse:
    return get_service().preview(request)


@app.post("/api/telemetry/write", response_model=TelemetryWriteResponse)
def telemetry_write(request: TelemetryWriteRequest) -> TelemetryWriteResponse:
    # La ruta expone errores operativos con codigos HTTP claros para que frontend
    # y scripts sepan si el bloqueo viene de politica local o de la red remota.
    try:
        return get_service().write(request)
    except ControlledWriteRejected as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ThingSpeakUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
