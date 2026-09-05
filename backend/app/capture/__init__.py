"""Camera capture abstraction.

The design page's "Take photo" button triggers whatever camera is configured
here (a ceiling-mounted rig over the design table, eventually). Real drivers
(USB / gphoto2 / IP camera) register as ``CaptureSource`` implementations; the
default ``none`` source raises ``CaptureNotConfigured`` and the endpoint returns
501.
"""

from __future__ import annotations

from functools import lru_cache

from app.capture.base import CaptureError, CaptureNotConfigured, CaptureSource
from app.capture.null_source import NullCaptureSource
from app.config import get_settings

_SOURCES: dict[str, type[CaptureSource]] = {
    "none": NullCaptureSource,
}


def register_source(name: str, source_cls: type[CaptureSource]) -> None:
    _SOURCES[name] = source_cls


@lru_cache
def get_capture_source() -> CaptureSource:
    name = get_settings().capture_source
    source_cls = _SOURCES.get(name)
    if source_cls is None:
        return NullCaptureSource(reason=f"unknown capture source {name!r}")
    return source_cls()


__all__ = [
    "CaptureError",
    "CaptureNotConfigured",
    "CaptureSource",
    "get_capture_source",
    "register_source",
]
