// Minimal hash navigation — no router library (see frontend/CLAUDE.md).
export function navigate(to: string) {
  window.location.hash = to
}
