// Shared visual vocabulary for layer roles — used by the component list and the
// schematic so a component reads the same in both.
export const ROLE_COLORS: Record<string, string> = {
  frame: '#8a5a2b',
  glazing: '#9fc7e0',
  fillet: '#c8a049',
  mat: '#e2dccf',
  art: '#b46b8b',
  spacer: '#9aa0a6',
  substrate: '#a8b39a',
  backing: '#8d8d8d',
  accent: '#7a6f9b',
}

export function roleColor(role: string): string {
  return ROLE_COLORS[role] ?? '#c9c9c9'
}
