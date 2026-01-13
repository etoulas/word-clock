"""
Built-in 5x5 pixel font for the word clock.
Includes A-Z and German umlauts (Ä, Ö, Ü).
Each character is a 5x5 bitmap stored as a list of 5 integers (rows).
"""
from __future__ import annotations

# 5x5 pixel font - each row is a 5-bit integer, MSB is leftmost pixel
FONT_5X5 = {
    'A': [0b01110, 0b10001, 0b11111, 0b10001, 0b10001],
    'B': [0b11110, 0b10001, 0b11110, 0b10001, 0b11110],
    'C': [0b01111, 0b10000, 0b10000, 0b10000, 0b01111],
    'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b11110],
    'E': [0b11111, 0b10000, 0b11110, 0b10000, 0b11111],
    'F': [0b11111, 0b10000, 0b11110, 0b10000, 0b10000],
    'G': [0b01111, 0b10000, 0b10011, 0b10001, 0b01110],
    'H': [0b10001, 0b10001, 0b11111, 0b10001, 0b10001],
    'I': [0b11111, 0b00100, 0b00100, 0b00100, 0b11111],
    'J': [0b00111, 0b00010, 0b00010, 0b10010, 0b01100],
    'K': [0b10001, 0b10010, 0b11100, 0b10010, 0b10001],
    'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    'M': [0b10001, 0b11011, 0b10101, 0b10001, 0b10001],
    'N': [0b10001, 0b11001, 0b10101, 0b10011, 0b10001],
    'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b01110],
    'P': [0b11110, 0b10001, 0b11110, 0b10000, 0b10000],
    'Q': [0b01110, 0b10001, 0b10101, 0b10010, 0b01101],
    'R': [0b11110, 0b10001, 0b11110, 0b10010, 0b10001],
    'S': [0b01111, 0b10000, 0b01110, 0b00001, 0b11110],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100],
    'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'V': [0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    'W': [0b10001, 0b10001, 0b10101, 0b11011, 0b10001],
    'X': [0b10001, 0b01010, 0b00100, 0b01010, 0b10001],
    'Y': [0b10001, 0b01010, 0b00100, 0b00100, 0b00100],
    'Z': [0b11111, 0b00010, 0b00100, 0b01000, 0b11111],
    # German umlauts
    'Ä': [0b10001, 0b01110, 0b10001, 0b11111, 0b10001],  # A with dots above
    'Ö': [0b10001, 0b01110, 0b10001, 0b10001, 0b01110],  # O with dots above
    'Ü': [0b10001, 0b00000, 0b10001, 0b10001, 0b01110],  # U with dots above
    # Space and fallback
    ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
}


def get_char_bitmap(char: str) -> list:
    """Get the 5x5 bitmap for a character."""
    return FONT_5X5.get(char.upper(), FONT_5X5.get(' '))


def draw_char(canvas, char: str, x: int, y: int, color: tuple):
    """
    Draw a character on a canvas using the built-in font.

    Args:
        canvas: The canvas to draw on (must have SetPixel method)
        char: The character to draw
        x: X position (top-left)
        y: Y position (top-left)
        color: RGB color tuple
    """
    bitmap = get_char_bitmap(char)
    if bitmap is None:
        return

    for row_idx, row_bits in enumerate(bitmap):
        for col_idx in range(5):
            if row_bits & (0b10000 >> col_idx):
                canvas.SetPixel(x + col_idx, y + row_idx, *color)


def preview_char(char: str):
    """Print ASCII preview of a character."""
    bitmap = get_char_bitmap(char)
    print(f"Character: {char}")
    for row_bits in bitmap:
        line = ""
        for col_idx in range(5):
            if row_bits & (0b10000 >> col_idx):
                line += "█"
            else:
                line += "·"
        print(line)
    print()


if __name__ == "__main__":
    # Preview all characters
    for char in "ESISCHAFÜFVIERTUBZÄÄZWÄNZGVORABHAUBIEISZWÖIDRÜFÜFISÄCHSISIBNIACHTINÜNIÖLZÄNIZWÖUFINAUHR":
        if char not in " ":
            preview_char(char)
