"""Pure moulding geometry helpers — no pricing, no shop config.

See docs/domain/moulding.md.
"""

from __future__ import annotations


def linear_feet_for_frame(finished_w_in: float, finished_h_in: float, face_width_in: float) -> float:
    # each side's outer length grows by the face width at both ends
    # (a mitre cutting allowance is deferred — see docs/OPEN_QUESTIONS.md)
    perimeter_in = 2 * (finished_w_in + face_width_in) + 2 * (finished_h_in + face_width_in)
    return perimeter_in / 12


def sight_size(glazing_w_in: float, glazing_h_in: float, rabbet_depth_in: float) -> tuple[float, float]:
    # STANDARD only: the lip covers rabbet_depth on every edge
    return (glazing_w_in - 2 * rabbet_depth_in, glazing_h_in - 2 * rabbet_depth_in)


def stack_fits(package_depth_in: float, rabbet_height_in: float) -> bool:
    # STANDARD only; FLOAT mouldings have no rabbet
    return package_depth_in <= rabbet_height_in


def float_finished_size(
    art_w_in: float, art_h_in: float, gap_in: float, face_width_in: float
) -> tuple[float, float]:
    # FLOAT only: gap comes from the DesignMoulding/MouldingLineInput, not the Moulding
    return (
        art_w_in + 2 * gap_in + 2 * face_width_in,
        art_h_in + 2 * gap_in + 2 * face_width_in,
    )
