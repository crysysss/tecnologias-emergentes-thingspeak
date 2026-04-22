from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from numbers import Real

from backend.config import CHANNEL_FIELDS, load_settings
from backend.fixtures import load_fixture_dataset
from backend.models import (
    ChannelFieldDefinition,
    ChannelInfo,
    HealthResponse,
    HistoryResponse,
    LatestResponse,
    TelemetryMeasurement,
    TelemetryPreviewRequest,
    TelemetryPreviewResponse,
    TelemetryWriteRequest,
    TelemetryWriteResponse,
)
from backend.thingspeak_client import (
    ThingSpeakClient,
    ThingSpeakUnavailable,
    ThingSpeakWriteRejected,
)


class ControlledWriteRejected(RuntimeError):
    """Raised when the application blocks a real write by policy or request state."""


def _format_decimal(value: float) -> str:
    # ThingSpeak espera cadenas con punto decimal. Este helper conserva precision
    # humana sin dejar ceros sobrantes como "52.400000".
    decimal_value = Decimal(str(value))
    formatted = format(decimal_value, "f")
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted or "0"


def _ensure_numeric(value: object) -> float:
    # Rechazamos bool porque en Python es subtipo de int y podria colarse como 0/1.
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("Todas las metricas deben ser numericas")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Todas las metricas deben ser numericas") from exc


def construir_payload_thingspeak_estabilidad(
    carga_cognitiva_pct: float,
    nivel_coherencia_pct: float,
    intensidad_emocional_pct: float,
    latencia_inferencia_ms: float,
    consumo_energetico_w: float,
) -> dict[str, str]:
    # Toda la validacion de dominio vive aqui para que preview y escritura real
    # compartan exactamente las mismas reglas.
    carga_cognitiva = _ensure_numeric(carga_cognitiva_pct)
    nivel_coherencia = _ensure_numeric(nivel_coherencia_pct)
    intensidad_emocional = _ensure_numeric(intensidad_emocional_pct)
    latencia_inferencia = _ensure_numeric(latencia_inferencia_ms)
    consumo_energetico = _ensure_numeric(consumo_energetico_w)

    if not 0 <= carga_cognitiva <= 100:
        raise ValueError("La carga cognitiva debe estar entre 0 y 100")
    if not 0 <= nivel_coherencia <= 100:
        raise ValueError("El nivel de coherencia debe estar entre 0 y 100")
    if not 0 <= intensidad_emocional <= 100:
        raise ValueError("La intensidad emocional debe estar entre 0 y 100")
    if latencia_inferencia < 0:
        raise ValueError("La latencia de inferencia no puede ser negativa")
    if consumo_energetico < 0:
        raise ValueError("El consumo energetico no puede ser negativo")

    return {
        "field1": _format_decimal(carga_cognitiva),
        "field2": _format_decimal(nivel_coherencia),
        "field3": _format_decimal(intensidad_emocional),
        "field4": _format_decimal(latencia_inferencia),
        "field5": _format_decimal(consumo_energetico),
    }


def _build_diagnostic_flags(
    cognitive_load_pct: float,
    coherence_level_pct: float,
    emotional_intensity_pct: float,
    inference_latency_ms: float,
    power_consumption_w: float,
) -> list[str]:
    # Estas banderas no son reglas oficiales de ThingSpeak: son ayudas de UI
    # para interpretar rapido el estado del androide.
    flags: list[str] = []
    if cognitive_load_pct >= 90:
        flags.append("Carga cognitiva critica")
    elif cognitive_load_pct >= 75:
        flags.append("Carga cognitiva elevada")

    if coherence_level_pct <= 70:
        flags.append("Coherencia muy baja")
    elif coherence_level_pct <= 80:
        flags.append("Coherencia en descenso")

    if emotional_intensity_pct >= 90:
        flags.append("Intensidad emocional muy alta")
    elif emotional_intensity_pct >= 80:
        flags.append("Intensidad emocional alta")

    if inference_latency_ms >= 220:
        flags.append("Latencia de inferencia critica")
    elif inference_latency_ms >= 180:
        flags.append("Latencia de inferencia elevada")

    if power_consumption_w >= 90:
        flags.append("Consumo energetico critico")
    elif power_consumption_w >= 80:
        flags.append("Consumo energetico alto")

    return flags


def _heuristic_state(flags: list[str]) -> str:
    # Unificamos muchas banderas en un estado compacto para frontend y logs.
    critical_hits = sum(
        "critica" in flag.lower() or "critico" in flag.lower()
        for flag in flags
    )
    if critical_hits >= 2:
        return "critical"
    if critical_hits == 1 or flags:
        return "warning"
    return "stable"


def _measurement_from_values(
    *,
    entry_id: int,
    recorded_at: datetime,
    source: str,
    cognitive_load_pct: float,
    coherence_level_pct: float,
    emotional_intensity_pct: float,
    inference_latency_ms: float,
    power_consumption_w: float,
) -> TelemetryMeasurement:
    # Convertimos cualquier origen de datos al mismo modelo para que frontend y
    # tests no tengan que conocer el formato nativo de ThingSpeak.
    flags = _build_diagnostic_flags(
        cognitive_load_pct,
        coherence_level_pct,
        emotional_intensity_pct,
        inference_latency_ms,
        power_consumption_w,
    )
    return TelemetryMeasurement(
        entry_id=entry_id,
        recorded_at=recorded_at,
        source=source,  # type: ignore[arg-type]
        cognitive_load_pct=cognitive_load_pct,
        coherence_level_pct=coherence_level_pct,
        emotional_intensity_pct=emotional_intensity_pct,
        inference_latency_ms=inference_latency_ms,
        power_consumption_w=power_consumption_w,
        stability_state=_heuristic_state(flags),  # type: ignore[arg-type]
        diagnostic_flags=flags,
        warnings=flags,
    )


def _request_template(base_url: str) -> str:
    return (
        f"{base_url}/update?"
        "api_key=<WRITE_API_KEY>&field1={field1}&field2={field2}"
        "&field3={field3}&field4={field4}&field5={field5}"
    )


def _build_preview_artifacts(
    request: TelemetryPreviewRequest,
) -> tuple[dict[str, str], TelemetryMeasurement]:
    # Preview y escritura real comparten este paso: validar, normalizar y generar
    # un resumen heuristico de la medicion.
    payload = construir_payload_thingspeak_estabilidad(
        carga_cognitiva_pct=request.cognitive_load_pct,
        nivel_coherencia_pct=request.coherence_level_pct,
        intensidad_emocional_pct=request.emotional_intensity_pct,
        latencia_inferencia_ms=request.inference_latency_ms,
        consumo_energetico_w=request.power_consumption_w,
    )
    measurement = _measurement_from_values(
        entry_id=0,
        recorded_at=datetime.now().astimezone(),
        source="fixture",
        cognitive_load_pct=request.cognitive_load_pct,
        coherence_level_pct=request.coherence_level_pct,
        emotional_intensity_pct=request.emotional_intensity_pct,
        inference_latency_ms=request.inference_latency_ms,
        power_consumption_w=request.power_consumption_w,
    )
    return payload, measurement


class TelemetryService:
    def __init__(self) -> None:
        self._settings = load_settings()
        self._client = ThingSpeakClient(self._settings)

    def _load_live_channel_metadata(self) -> dict | None:
        # Aprovechamos la respuesta de historial para obtener nombre y labels
        # reales del canal sin añadir un endpoint especifico extra.
        if not self._settings.thingspeak_allow_live_reads:
            return None
        try:
            payload = self._client.read_history(1)
        except ThingSpeakUnavailable:
            return None
        channel = payload.get("channel")
        return channel if isinstance(channel, dict) else None

    def get_health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            app_name=self._settings.app_name,
            source="auto" if self._settings.thingspeak_allow_live_reads else "fixture_only",
            detail=(
                "La API intenta leer ThingSpeak y solo usa el dataset local cuando la red falla."
                if self._settings.thingspeak_allow_live_reads
                else "Las lecturas en vivo estan deshabilitadas y solo se usa el dataset local."
            ),
            live_reads_enabled=self._settings.thingspeak_allow_live_reads,
            writes_enabled=self._settings.thingspeak_allow_write,
            fallback_samples=len(load_fixture_dataset()),
            channel_id=self._settings.thingspeak_channel_id,
        )

    def get_channel_info(self) -> ChannelInfo:
        # Si ThingSpeak responde, la UI enseña el nombre y labels exactos del canal
        # configurado. Si no, cae a una descripcion local estable.
        live_channel_metadata = self._load_live_channel_metadata()

        def pick_live_text(key: str, default: str) -> str:
            if not live_channel_metadata:
                return default
            value = live_channel_metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            return default

        field_definitions = [
            ChannelFieldDefinition(
                key=field.key,
                label=pick_live_text(field.key, field.label),
                unit=field.unit,
                description=field.description,
                min_value=field.min_value,
                max_value=field.max_value,
            )
            for field in CHANNEL_FIELDS
        ]
        return ChannelInfo(
            channel_id=self._settings.thingspeak_channel_id,
            name=pick_live_text("name", "Telemetria Androide IA - NeuroBotics"),
            author="mwa0000041180118",
            access="Public",
            description=pick_live_text(
                "description",
                (
                    "Canal publico para la monitorizacion en tiempo real del rendimiento, "
                    "estabilidad cognitiva y estado emocional de los androides asistentes."
                ),
            ),
            fields=field_definitions,
            live_reads_enabled=self._settings.thingspeak_allow_live_reads,
            writes_enabled=self._settings.thingspeak_allow_write,
            read_source_mode="auto" if self._settings.thingspeak_allow_live_reads else "fixture_only",
        )

    def get_history(self, limit: int) -> HistoryResponse:
        # La app distingue cuatro estados:
        # 1. live_data: ThingSpeak responde con mediciones utiles.
        # 2. live_empty: el canal existe pero aun no tiene muestras completas.
        # 3. fixture_fallback: la red falla y se usa el dataset de la practica.
        # 4. fixture_only: la lectura en vivo esta deshabilitada por configuracion.
        safe_limit = max(1, min(limit, 50))
        if self._settings.thingspeak_allow_live_reads:
            try:
                payload = self._client.read_history(safe_limit)
                return self._history_from_thingspeak_payload(payload, safe_limit)
            except ThingSpeakUnavailable as exc:
                return self._history_from_fixture(
                    safe_limit,
                    channel_state="fixture_fallback",
                    detail="ThingSpeak no respondio en vivo y se usa el dataset local de la practica.",
                    reason=str(exc),
                )
        return self._history_from_fixture(
            safe_limit,
            channel_state="fixture_only",
            detail="Las lecturas en vivo estan deshabilitadas por configuracion.",
            reason="Las lecturas en vivo estan deshabilitadas por configuracion.",
        )

    def get_latest(self) -> LatestResponse:
        # latest reutiliza history(limit=1) para no duplicar logica de estados.
        history = self.get_history(limit=1)
        measurement = history.measurements[0] if history.measurements else None
        return LatestResponse(
            source=history.source,
            channel_state=history.channel_state,
            detail=history.detail,
            fallback_reason=history.fallback_reason,
            measurement=measurement,
        )

    def preview(self, request: TelemetryPreviewRequest) -> TelemetryPreviewResponse:
        payload, measurement = _build_preview_artifacts(request)
        return TelemetryPreviewResponse(
            mode="preview_only",
            writes_enabled=self._settings.thingspeak_allow_write,
            payload=payload,
            request_template=_request_template(self._settings.thingspeak_base_url),
            warnings=[
                "Preview generado: este endpoint nunca escribe en ThingSpeak."
            ]
            + measurement.diagnostic_flags,
            heuristic_state=measurement.stability_state,
            detail="Payload validado localmente. No se ha enviado ninguna escritura real.",
        )

    def write(self, request: TelemetryWriteRequest) -> TelemetryWriteResponse:
        # La confirmacion interactiva se ha retirado porque este flujo apunta al
        # canal de pruebas. La barrera real queda en la configuracion local:
        # si el backend no tiene permisos de escritura, la operacion se bloquea.
        if not self._settings.thingspeak_allow_write:
            raise ControlledWriteRejected(
                "Las escrituras reales estan deshabilitadas por configuracion."
            )

        payload, measurement = _build_preview_artifacts(request)

        try:
            entry_id = self._client.write_fields(payload)
        except ThingSpeakWriteRejected as exc:
            raise ControlledWriteRejected(str(exc)) from exc

        return TelemetryWriteResponse(
            mode="live_write",
            writes_enabled=self._settings.thingspeak_allow_write,
            channel_id=self._settings.thingspeak_channel_id,
            entry_id=entry_id,
            payload=payload,
            request_template=_request_template(self._settings.thingspeak_base_url),
            warnings=measurement.diagnostic_flags,
            heuristic_state=measurement.stability_state,
            detail=(
                "Escritura real confirmada y enviada al canal configurado. "
                f"ThingSpeak devolvio entry_id={entry_id}."
            ),
        )

    def _history_from_fixture(
        self,
        limit: int,
        *,
        channel_state: str,
        detail: str,
        reason: str | None,
    ) -> HistoryResponse:
        # El fixture replica el dataset del PDF para que la app siga siendo
        # demostrable incluso si ThingSpeak no responde.
        rows = load_fixture_dataset()[:limit]
        measurements = [
            _measurement_from_values(
                entry_id=row["entry_id"],
                recorded_at=datetime.fromisoformat(row["recorded_at"].replace("Z", "+00:00")),
                source="fixture",
                cognitive_load_pct=row["cognitive_load_pct"],
                coherence_level_pct=row["coherence_level_pct"],
                emotional_intensity_pct=row["emotional_intensity_pct"],
                inference_latency_ms=row["inference_latency_ms"],
                power_consumption_w=row["power_consumption_w"],
            )
            for row in rows
        ]
        return HistoryResponse(
            source="fixture",
            channel_state=channel_state,  # type: ignore[arg-type]
            count=len(measurements),
            detail=detail,
            fallback_reason=reason,
            measurements=measurements,
        )

    def _history_from_thingspeak_payload(self, payload: dict, limit: int) -> HistoryResponse:
        # ThingSpeak puede devolver feeds vacios o filas incompletas. Eso no es un
        # error de red: es un estado distinto que debemos reflejar como live_empty.
        feed_rows = payload.get("feeds", [])[:limit]
        measurements: list[TelemetryMeasurement] = []
        for row in feed_rows:
            try:
                measurements.append(
                    _measurement_from_values(
                        entry_id=int(row["entry_id"]),
                        recorded_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                        source="live",
                        cognitive_load_pct=float(row["field1"]),
                        coherence_level_pct=float(row["field2"]),
                        emotional_intensity_pct=float(row["field3"]),
                        inference_latency_ms=float(row["field4"]),
                        power_consumption_w=float(row["field5"]),
                    )
                )
            except (KeyError, TypeError, ValueError, InvalidOperation):
                continue

        if not measurements:
            return HistoryResponse(
                source="live",
                channel_state="live_empty",
                count=0,
                detail="ThingSpeak responde correctamente, pero el canal todavia no tiene mediciones completas.",
                fallback_reason=None,
                measurements=[],
            )

        return HistoryResponse(
            source="live",
            channel_state="live_data",
            count=len(measurements),
            detail="Lectura en vivo desde ThingSpeak.",
            fallback_reason=None,
            measurements=measurements,
        )
