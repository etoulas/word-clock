"""
Display renderer for the 64x64 LED matrix word clock.
Maps the 11x10 character grid to the physical LED panel.
"""

from dataclasses import dataclass


@dataclass
class DisplayConfig:
    """Configuration for the LED matrix display."""
    panel_width: int = 64
    panel_height: int = 64

    # Grid dimensions (characters)
    grid_cols: int = 11
    grid_rows: int = 10

    # Character block size (pixels per character)
    char_width: int = 5
    char_height: int = 5

    # Spacing between characters
    char_spacing_x: int = 1
    char_spacing_y: int = 1

    # Colors (RGB tuples)
    color_on: tuple[int, int, int] = (255, 255, 255)  # White for lit letters
    color_off: tuple[int, int, int] = (0, 0, 0)       # Off
    color_dim: tuple[int, int, int] = (20, 20, 20)    # Dim for unlit letters (optional)
    color_dot: tuple[int, int, int] = (255, 255, 255) # Color for minute dots

    # Whether to show dim letters for unlit characters
    show_dim_letters: bool = False

    # Corner dot positions (relative to panel edges)
    dot_margin: int = 1
    dot_size: int = 2


class DisplayRenderer:
    """Renders the word clock display on the LED matrix."""

    def __init__(self, config: DisplayConfig = None):
        self.config = config or DisplayConfig()
        self._calculate_offsets()

    def _calculate_offsets(self):
        """Calculate the starting offset to center the grid on the panel."""
        cfg = self.config

        # Total grid size in pixels
        grid_pixel_width = (cfg.grid_cols * cfg.char_width +
                           (cfg.grid_cols - 1) * cfg.char_spacing_x)
        grid_pixel_height = (cfg.grid_rows * cfg.char_height +
                            (cfg.grid_rows - 1) * cfg.char_spacing_y)

        # Center offset
        self.offset_x = (cfg.panel_width - grid_pixel_width) // 2
        self.offset_y = (cfg.panel_height - grid_pixel_height) // 2

    def get_char_pixel_bounds(self, row: int, col: int) -> tuple[int, int, int, int]:
        """
        Get the pixel bounds for a character at grid position (row, col).

        Returns:
            (x_start, y_start, x_end, y_end) - inclusive bounds
        """
        cfg = self.config

        x_start = self.offset_x + col * (cfg.char_width + cfg.char_spacing_x)
        y_start = self.offset_y + row * (cfg.char_height + cfg.char_spacing_y)
        x_end = x_start + cfg.char_width - 1
        y_end = y_start + cfg.char_height - 1

        return (x_start, y_start, x_end, y_end)

    def get_dot_positions(self, num_dots: int) -> list[tuple[int, int, int, int]]:
        """
        Get pixel bounds for minute indicator dots.

        Args:
            num_dots: Number of dots to show (0-4)

        Returns:
            List of (x_start, y_start, x_end, y_end) bounds for each dot
        """
        cfg = self.config
        positions = []

        # Corner positions: top-left, top-right, bottom-right, bottom-left
        corners = [
            (cfg.dot_margin, cfg.dot_margin),  # Top-left
            (cfg.panel_width - cfg.dot_margin - cfg.dot_size, cfg.dot_margin),  # Top-right
            (cfg.panel_width - cfg.dot_margin - cfg.dot_size,
             cfg.panel_height - cfg.dot_margin - cfg.dot_size),  # Bottom-right
            (cfg.dot_margin, cfg.panel_height - cfg.dot_margin - cfg.dot_size),  # Bottom-left
        ]

        for i in range(min(num_dots, 4)):
            x, y = corners[i]
            positions.append((x, y, x + cfg.dot_size - 1, y + cfg.dot_size - 1))

        return positions

    def render_to_matrix(self, matrix, lit_positions: set[tuple[int, int]],
                         num_dots: int, grid: list[str] = None):
        """
        Render the clock display to an RGB matrix.

        Args:
            matrix: rgbmatrix.RGBMatrix instance
            lit_positions: Set of (row, col) positions to illuminate
            num_dots: Number of minute dots (0-4)
            grid: Optional character grid (for dim letter display)
        """
        cfg = self.config

        # Clear the matrix
        matrix.Clear()

        # Draw lit characters as solid blocks
        for row, col in lit_positions:
            x1, y1, x2, y2 = self.get_char_pixel_bounds(row, col)
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    matrix.SetPixel(x, y, *cfg.color_on)

        # Optionally draw dim letters for unlit positions
        if cfg.show_dim_letters and grid:
            for row in range(cfg.grid_rows):
                for col in range(cfg.grid_cols):
                    if (row, col) not in lit_positions:
                        x1, y1, x2, y2 = self.get_char_pixel_bounds(row, col)
                        for x in range(x1, x2 + 1):
                            for y in range(y1, y2 + 1):
                                matrix.SetPixel(x, y, *cfg.color_dim)

        # Draw minute dots
        dot_positions = self.get_dot_positions(num_dots)
        for x1, y1, x2, y2 in dot_positions:
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    matrix.SetPixel(x, y, *cfg.color_dot)

    def render_to_canvas(self, canvas, lit_positions: set[tuple[int, int]],
                         num_dots: int):
        """
        Render to a canvas (for double-buffering).

        Args:
            canvas: rgbmatrix canvas instance
            lit_positions: Set of (row, col) positions to illuminate
            num_dots: Number of minute dots (0-4)
        """
        cfg = self.config

        # Clear canvas
        canvas.Clear()

        # Draw lit characters
        for row, col in lit_positions:
            x1, y1, x2, y2 = self.get_char_pixel_bounds(row, col)
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    canvas.SetPixel(x, y, *cfg.color_on)

        # Draw minute dots
        dot_positions = self.get_dot_positions(num_dots)
        for x1, y1, x2, y2 in dot_positions:
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    canvas.SetPixel(x, y, *cfg.color_dot)

        return canvas


def preview_display(lit_positions: set[tuple[int, int]], num_dots: int,
                   config: DisplayConfig = None):
    """
    Print an ASCII preview of the display for debugging.
    """
    cfg = config or DisplayConfig()
    renderer = DisplayRenderer(cfg)

    # Create a simple grid representation
    display = [['·' for _ in range(cfg.panel_width)] for _ in range(cfg.panel_height)]

    # Mark lit characters
    for row, col in lit_positions:
        x1, y1, x2, y2 = renderer.get_char_pixel_bounds(row, col)
        for x in range(x1, min(x2 + 1, cfg.panel_width)):
            for y in range(y1, min(y2 + 1, cfg.panel_height)):
                display[y][x] = '█'

    # Mark dots
    dot_positions = renderer.get_dot_positions(num_dots)
    for x1, y1, x2, y2 in dot_positions:
        for x in range(x1, min(x2 + 1, cfg.panel_width)):
            for y in range(y1, min(y2 + 1, cfg.panel_height)):
                display[y][x] = '●'

    # Print (scaled down for readability)
    print("\n64x64 Display Preview (scaled):")
    for y in range(0, cfg.panel_height, 2):
        line = ""
        for x in range(0, cfg.panel_width, 1):
            line += display[y][x]
        print(line)


if __name__ == "__main__":
    from word_grid import get_words_for_time, get_minute_dots, get_lit_positions

    # Test rendering
    hour, minute = 14, 47  # 2:47 PM - "Es isch viert vor drü" + 2 dots

    words = get_words_for_time(hour, minute)
    positions = set(get_lit_positions(words))
    dots = get_minute_dots(minute)

    print(f"Time: {hour}:{minute:02d}")
    print(f"Words: {' '.join(words)}")
    print(f"Dots: {dots}")

    preview_display(positions, dots)
