import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import { api } from '../api/client'
import type { ComponentInput, DesignComponent, DesignRead } from '../api/types'

// --- helpers -------------------------------------------------------------

function toInputs(components: DesignComponent[]): ComponentInput[] {
  const indexById = new Map(components.map((c, i) => [c.id, i]))
  return components.map((c) => ({
    id: c.id < 0 ? undefined : c.id, // negative id = not yet persisted
    kind: c.kind,
    params: c.params,
    layer_role: c.layer_role,
    product_id: c.product_id,
    parent_index:
      c.parent_component_id != null ? indexById.get(c.parent_component_id) ?? null : null,
  }))
}

let tempId = -1

function blankComponent(kind: string, layerRole: string): DesignComponent {
  return {
    id: tempId--,
    kind,
    sequence: 0,
    layer_role: layerRole,
    params: {},
    product_id: null,
    parent_component_id: null,
    product: null,
  }
}

// --- context -----------------------------------------------------------

type EditorValue = {
  design: DesignRead | null
  loading: boolean
  saving: boolean
  error: string | null
  selectedId: number | null
  select: (id: number | null) => void
  addComponent: (kind: string, layerRole: string) => void
  removeComponent: (id: number) => void
  moveComponent: (id: number, dir: -1 | 1) => void
  updateParams: (id: number, params: Record<string, unknown>) => void
  setProduct: (id: number, productId: number | null) => void
  updateArtwork: (patch: Record<string, unknown>) => void
  setStatus: (status: string) => void
}

const Ctx = createContext<EditorValue | null>(null)

export function DesignEditorProvider({
  designId,
  children,
}: {
  designId: number
  children: ReactNode
}) {
  const [design, setDesign] = useState<DesignRead | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const latestComponents = useRef<DesignComponent[] | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    api
      .getDesign(designId)
      .then((d) => {
        if (!cancelled) {
          setDesign(d)
          setError(null)
        }
      })
      .catch((e) => !cancelled && setError(String(e.message ?? e)))
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [designId])

  const flush = useCallback(async () => {
    const components = latestComponents.current
    if (!components) return
    latestComponents.current = null
    setSaving(true)
    try {
      const updated = await api.patchDesign(designId, { components: toInputs(components) })
      setDesign(updated)
      setError(null)
    } catch (e) {
      setError(String((e as Error).message ?? e))
      // Reload authoritative state so the UI cannot drift after a rejected edit.
      try {
        setDesign(await api.getDesign(designId))
      } catch {
        /* leave error visible */
      }
    } finally {
      setSaving(false)
    }
  }, [designId])

  const scheduleSave = useCallback(
    (components: DesignComponent[]) => {
      latestComponents.current = components
      if (saveTimer.current) clearTimeout(saveTimer.current)
      saveTimer.current = setTimeout(flush, 450)
    },
    [flush],
  )

  // Local optimistic mutation, then debounced server reconcile.
  const mutateComponents = useCallback(
    (fn: (components: DesignComponent[]) => DesignComponent[]) => {
      setDesign((prev) => {
        if (!prev) return prev
        const next = fn(prev.components).map((c, i) => ({ ...c, sequence: i + 1 }))
        scheduleSave(next)
        return { ...prev, components: next }
      })
    },
    [scheduleSave],
  )

  const value = useMemo<EditorValue>(
    () => ({
      design,
      loading,
      saving,
      error,
      selectedId,
      select: setSelectedId,
      addComponent: (kind, layerRole) =>
        mutateComponents((cs) => [...cs, blankComponent(kind, layerRole)]),
      removeComponent: (id) => {
        setSelectedId((s) => (s === id ? null : s))
        mutateComponents((cs) => cs.filter((c) => c.id !== id))
      },
      moveComponent: (id, dir) =>
        mutateComponents((cs) => {
          const i = cs.findIndex((c) => c.id === id)
          const j = i + dir
          if (i < 0 || j < 0 || j >= cs.length) return cs
          const copy = [...cs]
          ;[copy[i], copy[j]] = [copy[j], copy[i]]
          return copy
        }),
      updateParams: (id, params) =>
        mutateComponents((cs) =>
          cs.map((c) => (c.id === id ? { ...c, params } : c)),
        ),
      setProduct: (id, productId) =>
        mutateComponents((cs) =>
          cs.map((c) => (c.id === id ? { ...c, product_id: productId } : c)),
        ),
      updateArtwork: async (patch) => {
        setSaving(true)
        try {
          const updated = await api.patchDesign(designId, { artwork: patch })
          setDesign(updated)
          setError(null)
        } catch (e) {
          setError(String((e as Error).message ?? e))
        } finally {
          setSaving(false)
        }
      },
      setStatus: async (status) => {
        setSaving(true)
        try {
          const updated = await api.patchDesign(designId, { status })
          setDesign(updated)
          setError(null)
        } catch (e) {
          setError(String((e as Error).message ?? e))
        } finally {
          setSaving(false)
        }
      },
    }),
    [design, loading, saving, error, selectedId, mutateComponents, designId],
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useDesignEditor(): EditorValue {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useDesignEditor must be used inside DesignEditorProvider')
  return ctx
}
