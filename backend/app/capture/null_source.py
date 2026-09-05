"""The default capture source: no camera."""

from __future__ import annotations

from app.capture.base import CaptureNotConfigured


class NullCaptureSource:
    name = "none"

    def __init__(self, reason: str | None = None) -> None:
        self._reason = reason or "no camera is configured (set FRAMESHOP_CAPTURE_SOURCE)"

    def capture(self) -> tuple[bytes, str]:
        raise CaptureNotConfigured(self._reason)
