from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any


def _load_json_dict(path: Path) -> dict[str, Any]:
    # El proyecto usa JSON de configuracion para que un profesor pueda descargarlo,
    # abrir `config/` y entender de inmediato contra que canal apunta la app.
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"El archivo de configuracion {path} debe contener un objeto JSON.")
    return payload


def _load_file_config() -> dict[str, Any]:
    # Orden de merge:
    # - `app_settings.json`: defaults versionados y seguros para distribuir.
    # - `app_settings.local.json`: secretos o overrides locales no versionados.
    root_dir = Path(__file__).resolve().parent.parent
    config_dir = root_dir / "config"
    versioned_config = _load_json_dict(config_dir / "app_settings.json")
    local_config = _load_json_dict(config_dir / "app_settings.local.json")
    return {**versioned_config, **local_config}


def _apply_env_file(
    env_path: Path,
    *,
    protected_keys: set[str],
    override_loaded_values: bool,
) -> None:
    # Mantenemos soporte para `.env` por compatibilidad, pero el camino principal
    # del proyecto ya vive en `config/`.
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or key in protected_keys:
            continue
        if override_loaded_values or key not in os.environ:
            os.environ[key] = value


def _load_local_env_files() -> None:
    root_dir = Path(__file__).resolve().parent.parent
    protected_keys = set(os.environ.keys())
    _apply_env_file(root_dir / ".env", protected_keys=protected_keys, override_loaded_values=False)
    _apply_env_file(root_dir / ".env.local", protected_keys=protected_keys, override_loaded_values=True)


def _normalize_env_name(name: str) -> str:
    return name.lower()


def _config_key_candidates(*names: str) -> list[str]:
    candidates: list[str] = []
    for name in names:
        normalized = _normalize_env_name(name)
        candidates.append(normalized)
        if normalized.startswith("backend_"):
            candidates.append(normalized.removeprefix("backend_"))
    return candidates


def _read_raw(config_values: dict[str, Any], *names: str) -> Any | None:
    # La prioridad final queda asi:
    # 1. Variables de entorno del proceso.
    # 2. `config/app_settings.local.json`.
    # 3. `config/app_settings.json`.
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    for key in _config_key_candidates(*names):
        if key in config_values:
            return config_values[key]
    return None


def _read_string(config_values: dict[str, Any], *names: str, default: str | None = None) -> str | None:
    value = _read_raw(config_values, *names)
    if value is None:
        return default
    stripped = str(value).strip()
    return stripped or default


def _read_bool(config_values: dict[str, Any], *names: str, default: bool) -> bool:
    value = _read_raw(config_values, *names)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _read_float(config_values: dict[str, Any], *names: str, default: float) -> float:
    value = _read_raw(config_values, *names)
    if value is None:
        return default
    return float(value)


def _read_int(config_values: dict[str, Any], *names: str, default: int) -> int:
    value = _read_raw(config_values, *names)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class ChannelFieldConfig:
    key: str
    label: str
    unit: str
    description: str
    min_value: float
    max_value: float | None


CHANNEL_FIELDS: tuple[ChannelFieldConfig, ...] = (
    ChannelFieldConfig(
        key="field1",
        label="Carga cognitiva",
        unit="%",
        description="Porcentaje de carga del modelo cognitivo del androide.",
        min_value=0.0,
        max_value=100.0,
    ),
    ChannelFieldConfig(
        key="field2",
        label="Nivel de coherencia",
        unit="0-100",
        description="Indice de coherencia de las respuestas del androide.",
        min_value=0.0,
        max_value=100.0,
    ),
    ChannelFieldConfig(
        key="field3",
        label="Intensidad emocional",
        unit="0-100",
        description="Intensidad afectiva estimada por la IA emocional.",
        min_value=0.0,
        max_value=100.0,
    ),
    ChannelFieldConfig(
        key="field4",
        label="Latencia de inferencia",
        unit="ms",
        description="Tiempo de inferencia del modelo durante la interaccion.",
        min_value=0.0,
        max_value=None,
    ),
    ChannelFieldConfig(
        key="field5",
        label="Consumo energetico",
        unit="W",
        description="Consumo energetico asociado al ciclo de inferencia.",
        min_value=0.0,
        max_value=None,
    ),
)


@dataclass(frozen=True)
class Settings:
    app_name: str
    backend_host: str
    backend_port: int
    frontend_origin: str
    thingspeak_base_url: str
    thingspeak_channel_id: int
    thingspeak_read_api_key: str | None
    thingspeak_write_api_key: str | None
    thingspeak_allow_live_reads: bool
    thingspeak_allow_write: bool
    thingspeak_request_timeout_seconds: float
    thingspeak_min_seconds_between_writes: float


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    # Cacheamos para no releer disco en cada request. Los tests limpian esta cache
    # cuando necesitan cambiar configuracion entre casos.
    _load_local_env_files()
    config_values = _load_file_config()
    read_api_key = _read_string(config_values, "THINGSPEAK_READ_API_KEY")
    write_api_key = _read_string(config_values, "THINGSPEAK_WRITE_API_KEY")
    return Settings(
        app_name="NeuroBotics Telemetry Safe Mode",
        backend_host=_read_string(config_values, "BACKEND_HOST", default="127.0.0.1") or "127.0.0.1",
        backend_port=_read_int(config_values, "BACKEND_PORT", default=8000),
        frontend_origin=_read_string(
            config_values,
            "BACKEND_FRONTEND_ORIGIN",
            default="http://127.0.0.1:4321",
        )
        or "http://127.0.0.1:4321",
        thingspeak_base_url=(
            _read_string(
                config_values,
                "THINGSPEAK_BASE_URL",
                "THINGSpeak_BASE_URL",
                default="https://api.thingspeak.com",
            )
            or "https://api.thingspeak.com"
        ).rstrip("/"),
        thingspeak_channel_id=_read_int(
            config_values,
            "THINGSPEAK_CHANNEL_ID",
            "THINGSpeak_CHANNEL_ID",
            default=3353980,
        ),
        thingspeak_read_api_key=read_api_key.strip() if read_api_key and read_api_key.strip() else None,
        thingspeak_write_api_key=write_api_key.strip() if write_api_key and write_api_key.strip() else None,
        thingspeak_allow_live_reads=_read_bool(
            config_values,
            "THINGSPEAK_ALLOW_LIVE_READS",
            "THINGSpeak_ALLOW_LIVE_READS",
            default=True,
        ),
        thingspeak_allow_write=_read_bool(
            config_values,
            "THINGSPEAK_ALLOW_WRITE",
            "THINGSpeak_ALLOW_WRITE",
            default=False,
        ),
        thingspeak_request_timeout_seconds=_read_float(
            config_values,
            "THINGSPEAK_REQUEST_TIMEOUT_SECONDS",
            "THINGSpeak_REQUEST_TIMEOUT_SECONDS",
            default=5.0,
        ),
        thingspeak_min_seconds_between_writes=_read_float(
            config_values,
            "THINGSPEAK_MIN_SECONDS_BETWEEN_WRITES",
            default=16.0,
        ),
    )
