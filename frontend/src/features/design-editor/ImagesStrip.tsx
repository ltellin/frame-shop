import { useRef, useState } from 'react'
import { api } from '../../api/client'
import { useDesignEditor } from '../../state/designEditor'

export function ImagesStrip() {
  const { design, reload } = useDesignEditor()
  const fileRef = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const [hint, setHint] = useState<string | null>(null)

  if (!design) return null

  const upload = async (file: File) => {
    setBusy(true)
    setHint(null)
    try {
      await api.uploadDesignImage(design.id, file)
      await reload()
    } catch (e) {
      setHint(String((e as Error).message ?? e))
    } finally {
      setBusy(false)
    }
  }

  const capture = async () => {
    setBusy(true)
    setHint(null)
    try {
      await api.captureDesignImage(design.id)
      await reload()
    } catch (e) {
      const status = (e as Error & { status?: number }).status
      setHint(
        status === 501
          ? 'No camera configured yet — add a photo instead.'
          : String((e as Error).message ?? e),
      )
    } finally {
      setBusy(false)
    }
  }

  const remove = async (imageId: string) => {
    setBusy(true)
    try {
      await api.deleteDesignImage(design.id, imageId)
      await reload()
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="images-strip">
      <div className="images-row">
        {design.images.map((img) => (
          <div key={img.id} className="thumb">
            <img src={img.url} alt="artwork" />
            <button className="thumb-x" title="Remove" onClick={() => remove(img.image_id)}>
              ✕
            </button>
          </div>
        ))}
        {design.images.length === 0 && <span className="muted">No photos yet</span>}
      </div>
      <div className="images-actions">
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          hidden
          onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])}
        />
        <button disabled={busy} onClick={() => fileRef.current?.click()}>
          Add photo
        </button>
        <button disabled={busy} onClick={capture}>
          📷 Take photo
        </button>
      </div>
      {hint && <p className="muted">{hint}</p>}
    </div>
  )
}
