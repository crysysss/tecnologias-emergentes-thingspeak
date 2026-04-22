from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

# Hacemos que el script sea ejecutable desde la raiz del proyecto sin depender
# de instalar el paquete backend en el entorno de Python.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import load_settings
from backend.fixtures import load_fixture_dataset
from backend.models import TelemetryWriteRequest
from backend.service import ControlledWriteRejected, TelemetryService
from backend.thingspeak_client import ThingSpeakUnavailable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publica de forma controlada las muestras del fixture en ThingSpeak."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Numero de muestras del fixture a publicar.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=None,
        help="Espera entre escrituras. Si se omite, usa la configuracion del proyecto.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    load_settings.cache_clear()
    settings = load_settings()
    service = TelemetryService()
    rows = load_fixture_dataset()[: max(0, args.count)]
    delay_seconds = (
        args.delay_seconds
        if args.delay_seconds is not None
        else settings.thingspeak_min_seconds_between_writes
    )

    print(
        {
            "channel_id": settings.thingspeak_channel_id,
            "rows_to_publish": len(rows),
            "writes_enabled": settings.thingspeak_allow_write,
            "delay_seconds": delay_seconds,
        }
    )

    if not rows:
        print("No hay filas seleccionadas para publicar.")
        return 0

    for index, row in enumerate(rows, start=1):
        # Reutilizamos el mismo request de la API para asegurar que CLI y backend
        # validan exactamente igual las metricas del dominio.
        request = TelemetryWriteRequest(
            cognitive_load_pct=row["cognitive_load_pct"],
            coherence_level_pct=row["coherence_level_pct"],
            emotional_intensity_pct=row["emotional_intensity_pct"],
            inference_latency_ms=row["inference_latency_ms"],
            power_consumption_w=row["power_consumption_w"],
        )

        try:
            result = service.write(request)
        except (ControlledWriteRejected, ThingSpeakUnavailable) as exc:
            print({"index": index, "status": "error", "message": str(exc)})
            return 1

        print(
            {
                "index": index,
                "entry_id": result.entry_id,
                "heuristic_state": result.heuristic_state,
                "payload": result.payload,
            }
        )

        if index < len(rows):
            # ThingSpeak suele imponer un intervalo minimo entre escrituras,
            # por eso dejamos la espera parametrizable y visible en el script.
            time.sleep(delay_seconds)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
