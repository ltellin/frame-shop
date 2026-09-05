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
import type { ComponentInput, DesignComponent, DesignRead, Provenance } from '../api/types'

function toInputs(components: DesignComponent[]): ComponentInput[] {
  const indexById = new Map(components.map((c, i) => [c.id, i]))
  return components.map((c) => ({
    id: c.id < 0 ? undefined : c.id,
    kind: c.kind,
    params: c.params,
    layer_role: c.layer_role,
    product_id: c.product_id,
    provenance: c.provenance,
    parent_index:
      c.parent_component_id != null ? (indexById.get(c.parent_component_id) ?? null) : null,
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
    provenance: 'shop',
    parent_component_id: null,
    product: null,
  }
}

type FieldPatch = Record<string, unknown>

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
  setProvenance: (id: number, provenance: Provenance) => void
  patchFields: (patch: FieldPatch) => Promise<void>
  reload: () => Promise<void>
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

  const reload = useCallback(async () => {
    setLoading(true)
    try {
      setDesign(await api.getDesign(designId))
      setError(null)
    } catch (e) {
      setError(String((e as Error).message ?? e))
    } finally {
      setLoading(false)
    }
  }, [designId])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    api
      .getDesign(designId)
      .then((d) => !cancelled && (setDesign(d), setError(null)))
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
      try {
        setDesign(await api.getDesign(designId))
      } catch {
        /* keep error */
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

  const patchFields = useCallback(
    async (patch: FieldPatch) => {
      setSaving(true)
      try {
        const updated = await api.patchDesign(designId, patch)
        setDesign(updated)
        setError(null)
      } catch (e) {
        setError(String((e as Error).message ?? e))
      } finally {
        setSaving(false)
      }
    },
    [designId],
  )

  const value = useMemo<EditorValue>(
    () => ({
      design,
      loading,
      saving,
      error,
      selectedId,
      select: setSelectedId,
      reload,
      patchFields,
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
        mutateComponents((cs) => cs.map((c) => (c.id === id ? { ...c, params } : c))),
      setProduct: (id, productId) =>
        mutateComponents((cs) => cs.map((c) => (c.id === id ? { ...c, product_id: productId } : c))),
      setProvenance: (id, provenance) =>
        mutateComponents((cs) =>
          cs.map((c) =>
            c.id === id
              ? { ...c, provenance, product_id: provenance === 'customer' ? null : c.product_id }
              : c,
          ),
        ),
    }),
    [design, loading, saving, error, selectedId, mutateComponents, patchFields, reload],
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useDesignEditor(): EditorValue {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useDesignEditor must be used inside DesignEditorProvider')
  return ctx
}
