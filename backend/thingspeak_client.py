from __future__ import annotations

import requests

from backend.config import Settings


class ThingSpeakUnavailable(RuntimeError):
    """Raised when the public ThingSpeak feed cannot be read."""


class ThingSpeakWriteRejected(RuntimeError):
    """Raised when a ThingSpeak write operation is not accepted."""


class ThingSpeakClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def read_history(self, limit: int) -> dict:
        # Si el canal es publico, la lectura puede funcionar incluso sin READ_API_KEY.
        params: dict[str, str | int] = {"results": limit}
        if self._settings.thingspeak_read_api_key:
            params["api_key"] = self._settings.thingspeak_read_api_key

        endpoint = (
            f"{self._settings.thingspeak_base_url}/channels/"
            f"{self._settings.thingspeak_channel_id}/feeds.json"
        )

        try:
            response = requests.get(
                endpoint,
                params=params,
                timeout=self._settings.thingspeak_request_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise ThingSpeakUnavailable(str(exc)) from exc

        feeds = payload.get("feeds")
        if not isinstance(feeds, list):
            raise ThingSpeakUnavailable("La respuesta de ThingSpeak no contiene 'feeds'.")
        return payload

    def write_fields(self, payload: dict[str, str]) -> int:
        # La escritura real vive en un metodo dedicado para que el servicio pueda
        # validar negocio y este cliente solo se ocupe de HTTP + parseo remoto.
        if not self._settings.thingspeak_write_api_key:
            raise ThingSpeakWriteRejected("No hay WRITE_API_KEY configurada para habilitar escrituras reales.")

        endpoint = f"{self._settings.thingspeak_base_url}/update"
        body = {
            "api_key": self._settings.thingspeak_write_api_key,
            **payload,
        }

        try:
            response = requests.post(
                endpoint,
                data=body,
                timeout=self._settings.thingspeak_request_timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ThingSpeakUnavailable(str(exc)) from exc

        # ThingSpeak responde con el entry_id creado. Si no devuelve un entero
        # positivo, tratamos la operacion como rechazada.
        entry_id = response.text.strip()
        try:
            parsed_entry_id = int(entry_id)
        except ValueError as exc:
            raise ThingSpeakWriteRejected(
                f"ThingSpeak devolvio una respuesta no numerica al escribir: {entry_id!r}"
            ) from exc

        if parsed_entry_id <= 0:
            raise ThingSpeakWriteRejected(
                "ThingSpeak rechazo la escritura y devolvio un identificador no valido."
            )

        return parsed_entry_id
