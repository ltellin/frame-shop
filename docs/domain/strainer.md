# Strainer

> Status: **modest first-pass notes — deliberately unresolved.** Do not model
> this yet.

---

# Definition

A **strainer** is an internal support frame installed behind a visible frame when
the visible moulding is too thin (or otherwise insufficient) to structurally
support the finished piece.

Moulding is the **visible perimeter frame**. A strainer serves a **structural
support role** and is not normally seen.

---

# Current stance

- **Do NOT model Strainer as a Moulding.** They play different roles.
- **Do NOT introduce a shared generic `ProfileGeometry` / `GenericProfileGeometry`
  abstraction** just because both a strainer and a moulding may be milled from
  wood profiles. If later requirements prove they genuinely need shared geometry
  behavior, extract it then — see the generic abstraction warning in
  [`../../AGENTS.md`](../../AGENTS.md).
- Treat Strainer as a **separate, unresolved support concept**.

---

# Possible future direction (not to build now)

A future system may recommend or require a strainer based on factors like:

- frame size
- moulding strength / profile
- glazing weight
- overall assembly weight

Do not build those rules now.

---

# Open Questions

Mirrored in [`../OPEN_QUESTIONS.md`](../OPEN_QUESTIONS.md):

- Should Strainer eventually be a separate Design component (a `DesignStrainer`,
  parallel to `DesignMoulding`)?
- What conditions should recommend or require a strainer?
- Does a strainer need its own geometry/material/fabrication model, and if so,
  how much does it actually share with Moulding?
