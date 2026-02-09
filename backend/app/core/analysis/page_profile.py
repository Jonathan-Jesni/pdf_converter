from dataclasses import dataclass, field

@dataclass
class PageProfile:
    page_number: int

    words: list = field(default_factory=list)
    images: list = field(default_factory=list)

    columns: int = 1
    column_x_ranges: list = field(default_factory=list)

    text_density: float = 0.0
    avg_font_size: float = 0.0

    has_form_alignment: bool = False
    has_table_grid: bool = False

    detected_mode: str = "semantic"
    reason: str = ""

    def decide_mode(self):
        if self.has_table_grid:
            self.detected_mode = "table"
            self.reason = "grid-aligned rows and columns"
            return

        if self.has_form_alignment:
            self.detected_mode = "form"
            self.reason = "repeated label-value alignment"
            return

        if self.columns > 1:
            self.detected_mode = "layout"
            self.reason = "multi-column text layout"
            return

        self.detected_mode = "semantic"
        self.reason = "normal flowing text"
