# ADR 0013 — Artwork images + camera-capture skeleton

- **Status:** accepted
- **Date:** 2026-09-05

## Context

A design should be able to carry photos of the artwork — for identifying which
piece goes with which order, and (the eventual goal) a ceiling-mounted camera
over the design table triggered from the design page. We want the skeleton now:
store an image with a design, and a button that triggers "the camera".

## Decision

- **Storage on disk.** Files at `<media_dir>/designs/<design_id>/<image_id>.<ext>`;
  `media_dir` from `FRAMESHOP_MEDIA_DIR` (default `./media`, gitignored).
  Metadata is the `design_image` table (`image_id`, `content_type`, `byte_size`,
  `source` = `upload | camera`, `is_primary`). `app/services/image_service.py`
  owns save / path / delete. `python-multipart` added for `UploadFile`.
- **API** under `/api/designs/{id}/images`: `POST` (multipart upload), `GET`
  (list — also in the design read model as `images`), `GET /{image_id}`
  (`FileResponse`), `DELETE /{image_id}`, `POST /capture`.
- **Capture abstraction** — `app/capture/`: a `CaptureSource` protocol
  (`capture() -> (bytes, content_type)`), `get_capture_source()` keyed by
  `FRAMESHOP_CAPTURE_SOURCE` (default `none` → `NullCaptureSource`, which raises
  `CaptureNotConfigured`). `POST /capture` returns **501** when unconfigured; the
  frontend button then shows "No camera configured yet — add a photo instead."

## Consequences

- The hardware integration point is a single module: a real driver (USB /
  gphoto2 / IP camera) registers with `register_source()` and implements
  `capture()`; nothing else changes.
- Images are per-design and survive on disk across restarts; the dev DB reset
  does not clear `media/` (harmless orphans — a cleanup pass is deferred).
- **You may not** store image bytes in the database or couple capture to a
  specific camera SDK in the endpoint layer, without revisiting this ADR.
- **Deferred:** thumbnail generation (Pillow), EXIF orientation, named views
  (front / back / damage), a browser `getUserMedia` fallback, carrying the
  primary image onto the Work Order snapshot.

## Alternatives considered

- **Bytes in the DB (BLOB)** — simplest to back up, but bloats the DB and the
  read paths; disk + a path table is the boring standard.
- **Browser `getUserMedia` only** — captures from the browser device's camera,
  not a triggered ceiling rig; useful later as a fallback, not the primary path.
