"""Storage for artwork images attached to a design.

Files live on disk under ``settings.media_dir``; metadata is the ``design_image``
table. Nothing here knows where the bytes came from (upload vs camera).
"""

from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import Design, DesignImage

_EXT_BY_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/heic": ".heic",
}


def _media_root() -> Path:
    return Path(get_settings().media_dir)


def _design_dir(design_id: int) -> Path:
    return _media_root() / "designs" / str(design_id)


def _ext_for(content_type: str, filename: str | None) -> str:
    if content_type in _EXT_BY_TYPE:
        return _EXT_BY_TYPE[content_type]
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[1].lower()
    return mimetypes.guess_extension(content_type or "") or ".bin"


def image_path(image: DesignImage) -> Path:
    ext = _ext_for(image.content_type, image.filename)
    return _design_dir(image.design_id) / f"{image.image_id}{ext}"


def save_image(
    session: Session,
    design: Design,
    *,
    data: bytes,
    filename: str | None,
    content_type: str,
    source: str,
) -> DesignImage:
    image = DesignImage(
        design_id=design.id,
        image_id=uuid.uuid4().hex,
        filename=filename,
        content_type=content_type or "application/octet-stream",
        byte_size=len(data),
        source=source,
        is_primary=not design.images,  # first image for the design
    )
    path = image_path(image)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    design.images.append(image)
    session.flush()
    return image


def get_image(session: Session, design_id: int, image_id: str) -> DesignImage | None:
    for img in session.get(Design, design_id).images if session.get(Design, design_id) else []:
        if img.image_id == image_id:
            return img
    return None


def delete_image(session: Session, image: DesignImage) -> None:
    path = image_path(image)
    path.unlink(missing_ok=True)
    was_primary = image.is_primary
    design = image.design
    session.delete(image)
    session.flush()
    if was_primary and design.images:
        design.images[0].is_primary = True
        session.flush()
