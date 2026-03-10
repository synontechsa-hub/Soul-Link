"""
Z-CAD Python — MaxRects Bin-Packing Algorithm

Implements the MAXRECTS algorithm (Jukka Jylänki, 2010).
This is significantly better than simple guillotine cuts.

Heuristic used: Best Short Side Fit (BSSF) — places each piece
into the free rectangle that minimises the shorter leftover side.
"""
from dataclasses import dataclass
from .models import Sheet, Piece, PlacedPiece, Job


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def area(self):
        return self.w * self.h

    def contains(self, other: "Rect") -> bool:
        return (self.x <= other.x and self.y <= other.y and
                self.x + self.w >= other.x + other.w and
                self.y + self.h >= other.y + other.h)


def _split_rect(free: Rect, placed: Rect) -> list[Rect]:
    """Split a free rectangle around a placed rectangle — guillotine split."""
    result = []
    # Right of placed
    if placed.x + placed.w < free.x + free.w:
        result.append(Rect(
            placed.x + placed.w, free.y,
            free.x + free.w - (placed.x + placed.w), free.h
        ))
    # Above placed (top remainder)
    if placed.y + placed.h < free.y + free.h:
        result.append(Rect(
            free.x, placed.y + placed.h,
            free.w, free.y + free.h - (placed.y + placed.h)
        ))
    # Left of placed
    if free.x < placed.x:
        result.append(Rect(
            free.x, free.y,
            placed.x - free.x, free.h
        ))
    # Below placed
    if free.y < placed.y:
        result.append(Rect(
            free.x, free.y,
            free.w, placed.y - free.y
        ))
    return result


def _prune_free_rects(free_rects: list[Rect]) -> list[Rect]:
    """Remove any free rectangle fully contained within another."""
    to_remove = set()
    for i, a in enumerate(free_rects):
        for j, b in enumerate(free_rects):
            if i != j and b.contains(a):
                to_remove.add(i)
                break
    return [r for i, r in enumerate(free_rects) if i not in to_remove]


def _score_bssf(free: Rect, pw: int, ph: int) -> tuple[int, int]:
    """Best Short Side Fit score — lower is better."""
    leftover_x = free.w - pw
    leftover_y = free.h - ph
    short = min(leftover_x, leftover_y)
    long_ = max(leftover_x, leftover_y)
    return (short, long_)


def pack_sheet(sheet: Sheet, pieces_flat: list[tuple["Piece", int]], kerf: int) -> tuple[list[PlacedPiece], list[tuple["Piece", int]]]:
    """
    Pack as many pieces as possible onto one sheet.

    pieces_flat: list of (Piece, index) tuples — one entry per individual piece
    kerf: blade kerf in mm (added to each placed piece's bounding box)

    Returns (placed_pieces, remaining_pieces)
    """
    free_rects = [Rect(0, 0, sheet.width, sheet.height)]
    placed_pieces: list[PlacedPiece] = []
    remaining = list(pieces_flat)

    # Sort by area descending for better packing
    remaining.sort(key=lambda x: x[0].width * x[0].height, reverse=True)

    placed_indices = set()

    changed = True
    while changed and remaining:
        changed = False
        best_score = (float('inf'), float('inf'))
        best_i = -1
        best_rect_i = -1
        best_pw = 0
        best_ph = 0
        best_rotated = False

        for i, (piece, _) in enumerate(remaining):
            if piece.width == 0 or piece.height == 0:
                placed_indices.add(i)
                continue

            for ri, free in enumerate(free_rects):
                # Try normal orientation
                pw, ph = piece.width + kerf, piece.height + kerf
                if pw <= free.w and ph <= free.h:
                    score = _score_bssf(free, pw, ph)
                    if score < best_score:
                        best_score = score
                        best_i = i
                        best_rect_i = ri
                        best_pw = pw
                        best_ph = ph
                        best_rotated = False

                # Try rotated
                if piece.can_rotate and not piece.grain_locked:
                    pw2, ph2 = piece.height + kerf, piece.width + kerf
                    if pw2 != pw or ph2 != ph:  # skip if same dimensions
                        if pw2 <= free.w and ph2 <= free.h:
                            score = _score_bssf(free, pw2, ph2)
                            if score < best_score:
                                best_score = score
                                best_i = i
                                best_rect_i = ri
                                best_pw = pw2
                                best_ph = ph2
                                best_rotated = True

        if best_i == -1:
            break  # Nothing more fits

        piece, _ = remaining[best_i]
        free = free_rects[best_rect_i]
        placed = Rect(free.x, free.y, best_pw, best_ph)

        # Actual piece dimensions (without kerf for drawing)
        draw_w = best_pw - kerf
        draw_h = best_ph - kerf

        placed_pieces.append(PlacedPiece(
            piece=piece,
            x=free.x,
            y=free.y,
            width=draw_w,
            height=draw_h,
            rotated=best_rotated,
        ))

        # Split free rectangles
        new_free = []
        for ri, fr in enumerate(free_rects):
            # Check overlap with placed rect
            if not (placed.x >= fr.x + fr.w or
                    placed.x + placed.w <= fr.x or
                    placed.y >= fr.y + fr.h or
                    placed.y + placed.h <= fr.y):
                new_free.extend(_split_rect(fr, placed))
            else:
                new_free.append(fr)

        free_rects = _prune_free_rects(new_free)

        remaining.pop(best_i)
        changed = True

    return placed_pieces, remaining


# Distinct colors for pieces
PIECE_COLORS = [
    (100, 149, 237),  # cornflower blue
    (144, 238, 144),  # light green
    (255, 182, 193),  # light pink
    (255, 218, 185),  # peach
    (221, 160, 221),  # plum
    (135, 206, 235),  # sky blue
    (255, 255, 153),  # light yellow
    (188, 143, 143),  # rosy brown
    (152, 251, 152),  # pale green
    (173, 216, 230),  # light blue
    (255, 160, 122),  # light salmon
    (240, 230, 140),  # khaki
]


def optimize(job: "Job") -> "Job":
    """
    Run the MaxRects optimization on a job.
    Populates job.layouts and job.unplaced.
    Returns the modified job.
    """
    from .models import SheetLayout

    job.layouts = []
    job.unplaced = []

    # Collect active sheets (respecting quantity)
    available_sheets: list[Sheet] = []
    for sheet in job.sheets:
        if sheet.active and sheet.width > 0 and sheet.height > 0:
            for _ in range(max(sheet.quantity, 1)):
                available_sheets.append(sheet)

    # Expand pieces by quantity
    pieces_flat: list[tuple[Piece, int]] = []
    color_map: dict[str, tuple] = {}
    for idx, piece in enumerate(job.pieces):
        if piece.quantity > 0 and piece.width > 0 and piece.height > 0:
            color = PIECE_COLORS[idx % len(PIECE_COLORS)]
            color_map[piece.id] = color
            for _ in range(piece.quantity):
                pieces_flat.append((piece, idx))

    remaining = pieces_flat

    for sheet in available_sheets:
        if not remaining:
            break

        placed, remaining = pack_sheet(sheet, list(remaining), job.blade_kerf)

        if placed:
            layout = SheetLayout(sheet=sheet, placed=placed)
            # Assign colors
            for pp in layout.placed:
                pp.color = color_map.get(pp.piece.id, (180, 180, 180))
            job.layouts.append(layout)

    job.unplaced = [piece for piece, _ in remaining]
    return job
