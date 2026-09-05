import type { ComponentKindMeta, JsonSchemaProp } from '../../api/types'

export type FieldSpec = {
  name: string
  label: string
  description?: string
  kind: 'enum' | 'number' | 'string'
  options?: string[]
  default?: unknown
}

function enumValues(prop: JsonSchemaProp): string[] | undefined {
  if (prop.enum?.length) return prop.enum
  const nested = prop.anyOf?.flatMap((a) => a.enum ?? [])
  return nested && nested.length ? nested : undefined
}

function classify(prop: JsonSchemaProp): FieldSpec['kind'] {
  if (enumValues(prop)) return 'enum'
  const types = [prop.type, ...(prop.anyOf?.map((a) => a.type) ?? [])]
  if (types.includes('number') || types.includes('integer')) return 'number'
  return 'string'
}

export function fieldsFor(meta: ComponentKindMeta): FieldSpec[] {
  const props = meta.param_schema.properties ?? {}
  return Object.entries(props).map(([name, prop]) => ({
    name,
    label: prop.title ?? name,
    description: prop.description,
    kind: classify(prop),
    options: enumValues(prop),
    default: prop.default,
  }))
}
