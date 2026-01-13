#!/usr/bin/env python3
"""
Bernese German Word Clock for 64x64 RGB LED Matrix.

A QLOCKTWO-style word clock displaying time in Bärndütsch (Bernese German).
Designed for the Seengreat RGB Matrix P3.0 64x64 (HUB75 interface).

Usage:
    sudo python3 clock.py [options]

Requires root privileges to access the GPIO pins.
"""
from __future__ import annotations

import argparse
import signal
import sys
import time
from datetime import datetime

from word_grid import get_words_for_time, get_minute_dots, get_lit_positions, GRID
from display import DisplayRenderer, DisplayConfig

# Try to import the RGB matrix library
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    HAS_MATRIX = True
except ImportError:
    HAS_MATRIX = False
    print("Warning: rgbmatrix library not found. Running in simulation mode.")


class WordClock:
    """Main word clock controller."""

    def __init__(self, args):
        self.args = args
        self.running = True

        # Setup display configuration
        dim = args.dim_brightness
        self.display_config = DisplayConfig(
            color_on=self._parse_color(args.color),
            color_dim=(dim, dim, dim),
            show_dim_letters=dim > 0,
        )
        self.renderer = DisplayRenderer(self.display_config)

        # Setup matrix if available
        if HAS_MATRIX and not args.simulate:
            self.matrix = self._create_matrix()
            self.canvas = self.matrix.CreateFrameCanvas()
        else:
            self.matrix = None
            self.canvas = None

        # Track last displayed time to avoid unnecessary updates
        self.last_minute = -1

    def _parse_color(self, color_str: str) -> tuple[int, int, int]:
        """Parse color from hex string or name."""
        color_map = {
            "white": (255, 255, 255),
            "warm": (255, 200, 150),
            "cool": (200, 220, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "orange": (255, 140, 0),
            "yellow": (255, 255, 0),
        }

        if color_str.lower() in color_map:
            return color_map[color_str.lower()]

        # Parse hex color
        if color_str.startswith("#"):
            color_str = color_str[1:]
        if len(color_str) == 6:
            return (
                int(color_str[0:2], 16),
                int(color_str[2:4], 16),
                int(color_str[4:6], 16),
            )

        return (255, 255, 255)  # Default white

    def _create_matrix(self) -> "RGBMatrix":
        """Create and configure the RGB matrix."""
        options = RGBMatrixOptions()

        # Panel configuration for 64x64 HUB75
        options.rows = 64
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1

        # Hardware configuration
        options.hardware_mapping = self.args.led_gpio_mapping
        options.row_address_type = self.args.led_row_addr_type
        options.multiplexing = self.args.led_multiplexing

        # Display quality settings
        options.pwm_bits = self.args.led_pwm_bits
        options.brightness = self.args.brightness
        options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = self.args.led_rgb_sequence

        # Performance settings
        options.gpio_slowdown = self.args.led_slowdown_gpio
        options.disable_hardware_pulsing = self.args.led_no_hardware_pulse
        options.show_refresh_rate = self.args.led_show_refresh

        # Pixel mapper for rotation if needed
        if self.args.led_pixel_mapper:
            options.pixel_mapper_config = self.args.led_pixel_mapper

        return RGBMatrix(options=options)

    def update_display(self, now: datetime = None):
        """Update the display with the current time."""
        if now is None:
            now = datetime.now()

        hour = now.hour
        minute = now.minute

        # Get words and positions
        words = get_words_for_time(hour, minute)
        positions = set(get_lit_positions(words))
        dots = get_minute_dots(minute)

        if self.matrix and self.canvas:
            # Render to canvas and swap
            self.renderer.render_to_canvas(self.canvas, GRID, positions, dots)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
        else:
            # Simulation mode - print to console
            self._print_simulation(hour, minute, words, positions, dots)

    def _print_simulation(self, hour: int, minute: int, words: list[str],
                         positions: set, dots: int):
        """Print simulation output to console."""
        # Clear screen
        print("\033[2J\033[H", end="")

        print("=" * 50)
        print(f"  BÄRNER WORT-UHR  |  {hour:02d}:{minute:02d}")
        print("=" * 50)
        print()

        # Corner dots
        dot_chars = ["○", "○", "○", "○"]
        for i in range(dots):
            dot_chars[i] = "●"

        print(f"    {dot_chars[0]}                       {dot_chars[1]}")
        print()

        # Word grid
        for row_idx, row in enumerate(GRID):
            line = "      "
            for col_idx, char in enumerate(row):
                if (row_idx, col_idx) in positions:
                    line += f"\033[1;37m{char}\033[0m "  # Bold white
                else:
                    line += f"\033[2;30m{char}\033[0m "  # Dim
            print(line)

        print()
        print(f"    {dot_chars[3]}                       {dot_chars[2]}")
        print()
        print(f"  → {' '.join(words)}")
        print()

    def run(self):
        """Main clock loop."""
        print("Starting Bernese Word Clock...")
        print("Press Ctrl+C to exit.\n")

        # Setup signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        while self.running:
            now = datetime.now()

            # Only update display when minute changes (or on first run)
            if now.minute != self.last_minute:
                self.update_display(now)
                self.last_minute = now.minute

            # Sleep until next second
            time.sleep(1.0 - (time.time() % 1.0))

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\nShutting down...")
        self.running = False
        if self.matrix:
            self.matrix.Clear()

    def cleanup(self):
        """Clean up resources."""
        if self.matrix:
            self.matrix.Clear()


def main():
    parser = argparse.ArgumentParser(
        description="Bernese German Word Clock for 64x64 RGB LED Matrix"
    )

    # Display options
    parser.add_argument(
        "--color", "-c",
        default="white",
        help="Letter color: white, warm, cool, red, green, blue, orange, yellow, or hex (#RRGGBB)"
    )
    parser.add_argument(
        "--brightness", "-b",
        type=int, default=50,
        help="Display brightness (1-100, default: 50)"
    )
    parser.add_argument(
        "--dim-brightness",
        type=int, default=40,
        help="Brightness of unlit letters (0-255, default: 40)"
    )
    parser.add_argument(
        "--simulate", "-s",
        action="store_true",
        help="Run in simulation mode (no hardware required)"
    )

    # LED matrix hardware options
    parser.add_argument(
        "--led-gpio-mapping",
        default="regular",
        help="GPIO mapping: regular, adafruit-hat, adafruit-hat-pwm (default: regular)"
    )
    parser.add_argument(
        "--led-pwm-bits",
        type=int, default=11,
        help="PWM bits (1-11, default: 11)"
    )
    parser.add_argument(
        "--led-pwm-lsb-nanoseconds",
        type=int, default=130,
        help="PWM LSB nanoseconds (default: 130)"
    )
    parser.add_argument(
        "--led-slowdown-gpio",
        type=int, default=1,
        help="GPIO slowdown (0-4, default: 1; use 4 for RPi 4, 0-1 for RPi 1)"
    )
    parser.add_argument(
        "--led-no-hardware-pulse",
        action="store_true",
        help="Disable hardware PWM"
    )
    parser.add_argument(
        "--led-row-addr-type",
        type=int, default=0,
        help="Row address type (0-4, default: 0)"
    )
    parser.add_argument(
        "--led-multiplexing",
        type=int, default=0,
        help="Multiplexing type (0-18, default: 0)"
    )
    parser.add_argument(
        "--led-rgb-sequence",
        default="RGB",
        help="RGB sequence (default: RGB)"
    )
    parser.add_argument(
        "--led-pixel-mapper",
        default="",
        help="Pixel mapper config (e.g., 'Rotate:90')"
    )
    parser.add_argument(
        "--led-show-refresh",
        action="store_true",
        help="Show refresh rate"
    )

    args = parser.parse_args()

    # Validate brightness
    args.brightness = max(1, min(100, args.brightness))

    # Run the clock
    clock = WordClock(args)
    try:
        clock.run()
    finally:
        clock.cleanup()


if __name__ == "__main__":
    main()
