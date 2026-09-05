from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.capture import CaptureNotConfigured, get_capture_source
from app.capture.base import CaptureError
from app.db.base import get_session
from app.services import design_service, image_service

router = APIRouter(prefix="/designs/{design_id}/images", tags=["design-images"])

_MAX_BYTES = 25 * 1024 * 1024


def _image_out(design_id: int, img) -> dict:
    return design_service.image_read_dict(design_id, img)


@router.get("")
def list_images(design_id: int, session: Session = Depends(get_session)) -> list[dict]:
    design = design_service.get_design(session, design_id)
    return [_image_out(design_id, img) for img in design.images]


@router.post("", status_code=201)
async def upload_image(
    design_id: int, file: UploadFile, session: Session = Depends(get_session)
) -> dict:
    design = design_service.get_design(session, design_id)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="image too large")
    img = image_service.save_image(
        session,
        design,
        data=data,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        source="upload",
    )
    session.commit()
    return _image_out(design_id, img)


@router.post("/capture", status_code=201)
def capture_image(design_id: int, session: Session = Depends(get_session)) -> dict:
    design = design_service.get_design(session, design_id)
    try:
        data, content_type = get_capture_source().capture()
    except CaptureNotConfigured as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from None
    except CaptureError as exc:
        raise HTTPException(status_code=502, detail=f"camera error: {exc}") from None
    img = image_service.save_image(
        session,
        design,
        data=data,
        filename="capture",
        content_type=content_type,
        source="camera",
    )
    session.commit()
    return _image_out(design_id, img)


@router.get("/{image_id}")
def get_image_file(
    design_id: int, image_id: str, session: Session = Depends(get_session)
) -> FileResponse:
    img = image_service.get_image(session, design_id, image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="image not found")
    path = image_service.image_path(img)
    if not path.exists():
        raise HTTPException(status_code=404, detail="image file missing")
    return FileResponse(path, media_type=img.content_type)


@router.delete("/{image_id}", status_code=204)
def delete_image(design_id: int, image_id: str, session: Session = Depends(get_session)) -> None:
    img = image_service.get_image(session, design_id, image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="image not found")
    image_service.delete_image(session, img)
    session.commit()
