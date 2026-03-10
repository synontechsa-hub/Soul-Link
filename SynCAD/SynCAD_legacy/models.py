"""
Z-CAD Python — Data Models
"""
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Sheet:
    """A stock sheet of material available for cutting."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    width: int = 0          # mm
    height: int = 0         # mm
    active: bool = True
    quantity: int = 1       # how many of this sheet type in stock
    buy_price: float = 0.0  # cost price per sheet (€)
    sell_price: float = 0.0 # sell price per sheet (€)
    thickness: float = 0.0  # mm
    label: str = ""         # optional label e.g. "4100x1200"

    @property
    def area(self) -> int:
        return self.width * self.height

    def display_label(self) -> str:
        if self.label:
            return self.label
        return f"{self.width} × {self.height} mm"


@dataclass
class Piece:
    """A rectangular piece that needs to be cut."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    quantity: int = 0       # how many needed
    width: int = 0          # mm
    height: int = 0         # mm
    can_rotate: bool = True # allow 90° rotation
    label: str = ""         # e.g. "Side panel left"
    grain_locked: bool = False  # if True, cannot rotate

    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass
class PlacedPiece:
    """A piece that has been placed onto a sheet layout."""
    piece: Piece
    x: int          # mm from left
    y: int          # mm from top
    width: int      # actual placed width (may be rotated)
    height: int     # actual placed height
    rotated: bool = False
    color: tuple = (100, 149, 237)  # cornflower blue default


@dataclass
class SheetLayout:
    """Result of placing pieces onto one physical sheet."""
    sheet: Sheet
    placed: list = field(default_factory=list)  # list of PlacedPiece
    waste_area: int = 0

    @property
    def used_area(self) -> int:
        return sum(p.width * p.height for p in self.placed)

    @property
    def efficiency(self) -> float:
        if self.sheet.area == 0:
            return 0.0
        return self.used_area / self.sheet.area * 100


@dataclass
class Job:
    """A complete cutting job."""
    name: str = "New Job"
    customer: str = ""
    notes: str = ""
    material_name: str = ""
    blade_kerf: int = 4     # mm — saw blade thickness
    hourly_rate: float = 0.0
    markup_percent: float = 0.0

    sheets: list = field(default_factory=list)   # list of Sheet
    pieces: list = field(default_factory=list)   # list of Piece

    # Results (populated after optimization)
    layouts: list = field(default_factory=list)  # list of SheetLayout
    unplaced: list = field(default_factory=list) # list of Piece that didn't fit

    @property
    def total_pieces_needed(self) -> int:
        return sum(p.quantity for p in self.pieces if p.quantity > 0)

    @property
    def total_pieces_placed(self) -> int:
        return sum(len(layout.placed) for layout in self.layouts)

    @property
    def sheets_used(self) -> int:
        return len(self.layouts)

    @property
    def total_material_cost(self) -> float:
        cost = 0.0
        for layout in self.layouts:
            cost += layout.sheet.buy_price
        return cost

    @property
    def total_sell_price(self) -> float:
        price = 0.0
        for layout in self.layouts:
            price += layout.sheet.sell_price
        if self.markup_percent > 0:
            price *= (1 + self.markup_percent / 100)
        return price

    @property
    def estimated_cuts(self) -> int:
        """Rough estimate: each piece needs ~2 cuts on average."""
        return self.total_pieces_placed * 2

    @property
    def estimated_labor_minutes(self) -> float:
        """~2 minutes per cut as a starting estimate."""
        return self.estimated_cuts * 2.0

    @property
    def estimated_labor_cost(self) -> float:
        return (self.estimated_labor_minutes / 60) * self.hourly_rate

    @property
    def overall_efficiency(self) -> float:
        total_used = sum(l.used_area for l in self.layouts)
        total_sheet = sum(l.sheet.area for l in self.layouts)
        if total_sheet == 0:
            return 0.0
        return total_used / total_sheet * 100
