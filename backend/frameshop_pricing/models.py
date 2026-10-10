"""Domain value objects for moulding pricing.

Mirrors docs/domain/{moulding,material,finish,extra,offering,design-moulding}.md.
Money is represented as plain floats — this doesn't resolve
docs/OPEN_QUESTIONS.md's still-open money-representation question, just a
pragmatic choice for this standalone package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MouldingType(str, Enum):
    STANDARD = "STANDARD"
    FLOAT = "FLOAT"


class MillingOrientation(str, Enum):
    FROM_BOARD_EDGE = "from_board_edge"
    FROM_BOARD_FACE = "from_board_face"


class JoineryMethod(str, Enum):
    UNDERPINNING = "underpinning"
    SPLINING = "splining"


@dataclass(frozen=True)
class Moulding:
    """A geometry / fabrication specification. See docs/domain/moulding.md.

    Carries no material, finish, embellishment, joinery, or price — only
    geometry and the pricing-input facts (tooling_work, waste_factor,
    source_lumber_size, optional minimum_footage_override).
    """

    name: str
    type: MouldingType
    face_width_in: float
    overall_height_in: float
    tooling_work: int  # one of 1, 2, 3, 5, 8
    waste_factor: float  # multiplier, >= 1.0
    # milling orientation -> (thickness_in, width_in) of the board it's milled from.
    # Explicit and shop-set, not computed from geometry — see ADR 0007.
    source_lumber_size: dict[MillingOrientation, tuple[float, float]]
    minimum_footage_override: float | None = None

    # STANDARD only
    rabbet_depth_in: float | None = None
    rabbet_height_in: float | None = None

    # FLOAT only
    internal_height_in: float | None = None
    float_board_thickness_in: float | None = None

    # Reference only — never read by the pricing engine. A path/filename
    # pointing at a cross-section diagram (e.g. a Fusion 360 export), for
    # visually matching a catalog entry to the real profile.
    diagram_path: str | None = None

    def __post_init__(self) -> None:
        if self.tooling_work not in (1, 2, 3, 5, 8):
            raise ValueError(f"tooling_work must be one of 1/2/3/5/8, got {self.tooling_work!r}")
        if self.waste_factor < 1.0:
            raise ValueError(f"waste_factor must be >= 1.0, got {self.waste_factor!r}")
        if not self.source_lumber_size:
            raise ValueError("source_lumber_size must define at least one milling orientation")


@dataclass(frozen=True)
class Extra:
    """See docs/domain/extra.md. Its rate/pricing method live in
    PricingContext.extra_rates, not here, so new extras are pure data."""

    name: str


@dataclass(frozen=True)
class ExtraRate:
    method: str  # "per_length" | "flat"
    value: float


@dataclass(frozen=True)
class FinishRate:
    """Two-rate finish pricing: `base_rate_per_ft` covers the shop's minimum
    footage (setup/cleanup labor dominates a small job); `marginal_rate_per_ft`
    applies to footage beyond that minimum, since size matters much less once
    a piece is already being finished. See docs/decisions/0008-*.md."""

    base_rate_per_ft: float
    marginal_rate_per_ft: float

    def __post_init__(self) -> None:
        if self.marginal_rate_per_ft > self.base_rate_per_ft:
            raise ValueError(
                "marginal_rate_per_ft should not exceed base_rate_per_ft "
                f"(got marginal={self.marginal_rate_per_ft!r} > base={self.base_rate_per_ft!r})"
            )


@dataclass(frozen=True)
class Offering:
    """A size-agnostic component recipe with its own price.
    See docs/domain/offering.md and docs/decisions/0005-*.md."""

    name: str
    moulding: Moulding
    material: str
    finish: str
    extras: tuple[Extra, ...]
    menu_price_per_foot: float


@dataclass(frozen=True)
class MouldingLineInput:
    """One moulding line to price.

    Deliberately not a `DesignMoulding` — Design/DesignMoulding aren't
    specified yet. This is the narrow, stable input the pricing engine
    depends on; a future Design should build one of these from itself
    rather than the engine depending on Design's shape.
    """

    moulding: Moulding
    material: str
    finish: str
    extras: tuple[Extra, ...]
    finished_width_in: float
    finished_height_in: float
    milling_orientation: MillingOrientation = MillingOrientation.FROM_BOARD_EDGE
    joinery_method: JoineryMethod = JoineryMethod.UNDERPINNING
    source_offering: Offering | None = None
    non_offering_labor_charge_override: float | None = None
