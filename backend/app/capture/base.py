"""Capture source protocol + errors."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class CaptureError(Exception):
    """A configured camera failed to produce an image."""


class CaptureNotConfigured(CaptureError):
    """No camera is configured (the default state)."""


@runtime_checkable
class CaptureSource(Protocol):
    name: str

    def capture(self) -> tuple[bytes, str]:
        """Return (image_bytes, content_type). Raise CaptureError on failure."""
        ...
