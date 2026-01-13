"""
Display renderer for the 64x64 LED matrix word clock.
Maps the 11x10 character grid to the physical LED panel.
"""
from __future__ import annotations

from dataclasses import dataclass
import os

from pixel_font import draw_char

# Try to import graphics module for font rendering
try:
    from rgbmatrix import graphics
    HAS_GRAPHICS = True
except ImportError:
    HAS_GRAPHICS = False


@dataclass
class DisplayConfig:
    """Configuration for the LED matrix display."""
    panel_width: int = 64
    panel_height: int = 64

    # Grid dimensions (characters)
    grid_cols: int = 11
    grid_rows: int = 10

    # Colors (RGB tuples)
    color_on: tuple = (255, 255, 255)   # White for lit letters
    color_off: tuple = (0, 0, 0)        # Off
    color_dim: tuple = (15, 15, 15)     # Dim for unlit letters
    color_dot: tuple = (255, 255, 255)  # Color for minute dots

    # Whether to show dim letters for unlit characters
    show_dim_letters: bool = True

    # Corner dot size
    dot_size: int = 2

    # Font path (None = use built-in)
    font_path: str = None


class DisplayRenderer:
    """Renders the word clock display on the LED matrix."""

    def __init__(self, config: DisplayConfig = None):
        self.config = config or DisplayConfig()
        self.font = None
        self.font_width = 5
        self.font_height = 6
        self._load_font()
        self._calculate_layout()

    def _load_font(self):
        """Load the BDF font for rendering."""
        if not HAS_GRAPHICS:
            return

        # Try to find a suitable small font
        font_paths = [
            self.config.font_path,
            "/usr/share/fonts/misc/5x7.bdf",
            "/usr/share/fonts/X11/misc/5x7.bdf",
            # rpi-rgb-led-matrix fonts location
            "/opt/rpi-rgb-led-matrix/fonts/5x7.bdf",
            "/opt/rpi-rgb-led-matrix/fonts/4x6.bdf",
            "fonts/5x7.bdf",
            "fonts/4x6.bdf",
        ]

        for path in font_paths:
            if path and os.path.exists(path):
                self.font = graphics.Font()
                self.font.LoadFont(path)
                # Estimate font dimensions from path
                if "4x6" in path:
                    self.font_width = 4
                    self.font_height = 6
                elif "5x7" in path:
                    self.font_width = 5
                    self.font_height = 7
                elif "5x8" in path:
                    self.font_width = 5
                    self.font_height = 8
                elif "6x9" in path:
                    self.font_width = 6
                    self.font_height = 9
                break

    def _calculate_layout(self):
        """Calculate grid layout to fit 11x10 characters on 64x64 display."""
        cfg = self.config

        # Calculate spacing to distribute characters evenly
        # Total width needed: 11 chars * font_width + 10 gaps
        # We want this to fit in 64 pixels with some margin for dots

        # Leave 2 pixels on each side for corner dots
        usable_width = cfg.panel_width - 4
        usable_height = cfg.panel_height - 4

        # Calculate character cell size (including spacing)
        self.cell_width = usable_width // cfg.grid_cols   # ~5 pixels
        self.cell_height = usable_height // cfg.grid_rows  # ~6 pixels

        # Calculate starting offset to center the grid
        total_width = self.cell_width * cfg.grid_cols
        total_height = self.cell_height * cfg.grid_rows
        self.offset_x = (cfg.panel_width - total_width) // 2
        self.offset_y = (cfg.panel_height - total_height) // 2

    def get_char_position(self, row: int, col: int) -> tuple:
        """Get the pixel position for a character at grid position."""
        x = self.offset_x + col * self.cell_width
        # Font baseline is at bottom, so add cell_height
        y = self.offset_y + row * self.cell_height + self.cell_height - 1
        return (x, y)

    def get_dot_positions(self, num_dots: int) -> list:
        """Get pixel positions for minute indicator dots (corners)."""
        cfg = self.config
        size = cfg.dot_size
        positions = []

        # Corner positions: top-left, top-right, bottom-right, bottom-left
        corners = [
            (0, 0),                                          # Top-left
            (cfg.panel_width - size, 0),                     # Top-right
            (cfg.panel_width - size, cfg.panel_height - size),  # Bottom-right
            (0, cfg.panel_height - size),                    # Bottom-left
        ]

        for i in range(min(num_dots, 4)):
            positions.append(corners[i])

        return positions

    def render_to_canvas(self, canvas, grid: list, lit_positions: set, num_dots: int):
        """
        Render the clock display to a canvas.

        Args:
            canvas: rgbmatrix canvas instance
            grid: The character grid (list of strings)
            lit_positions: Set of (row, col) positions to illuminate brightly
            num_dots: Number of minute dots (0-4)
        """
        cfg = self.config

        # Clear canvas
        canvas.Clear()

        # Use built-in pixel font for guaranteed umlaut support
        for row_idx, row in enumerate(grid):
            for col_idx, char in enumerate(row):
                x = self.offset_x + col_idx * self.cell_width
                y = self.offset_y + row_idx * self.cell_height

                if (row_idx, col_idx) in lit_positions:
                    draw_char(canvas, char, x, y, cfg.color_on)
                elif cfg.show_dim_letters:
                    draw_char(canvas, char, x, y, cfg.color_dim)

        # Draw minute dots
        dot_positions = self.get_dot_positions(num_dots)
        for x, y in dot_positions:
            for dx in range(cfg.dot_size):
                for dy in range(cfg.dot_size):
                    canvas.SetPixel(x + dx, y + dy, *cfg.color_dot)

        return canvas


def preview_display(grid: list, lit_positions: set, num_dots: int):
    """Print an ASCII preview of the display for debugging."""
    print("\nDisplay Preview:")

    # Corner dots indicator
    dot_chars = ["○", "○", "○", "○"]
    for i in range(num_dots):
        dot_chars[i] = "●"

    print(f"  {dot_chars[0]}                     {dot_chars[1]}")
    print()

    for row_idx, row in enumerate(grid):
        line = "  "
        for col_idx, char in enumerate(row):
            if (row_idx, col_idx) in lit_positions:
                line += char + " "
            else:
                line += "· "
        print(line)

    print()
    print(f"  {dot_chars[3]}                     {dot_chars[2]}")


if __name__ == "__main__":
    from word_grid import get_words_for_time, get_minute_dots, get_lit_positions, GRID

    # Test rendering
    hour, minute = 14, 47

    words = get_words_for_time(hour, minute)
    positions = set(get_lit_positions(words))
    dots = get_minute_dots(minute)

    print(f"Time: {hour}:{minute:02d}")
    print(f"Words: {' '.join(words)}")
    print(f"Dots: {dots}")

    preview_display(GRID, positions, dots)
