"""
Bernese German (Bärndütsch) word grid for QLOCKTWO-style word clock.
Based on the original QLOCKTWO Swiss German layout.
"""
from __future__ import annotations

# The 11x10 letter grid
# Each row has 11 characters
GRID = [
    "ESKISCHAFÜF",   # ES ISCH, FÜF
    "VIERTUBFZÄÄ",   # VIERT, ZÄÄ
    "ZWÄNZGSIVOR",   # ZWÄNZG, VOR
    "ABOHAUBIEGE",   # AB, HAUBI
    "EISZWÖISDRÜ",   # EIS, ZWÖI, DRÜ
    "VIERIFÜFIQT",   # VIERI, FÜFI
    "SÄCHSISIBNI",   # SÄCHSI, SIBNI
    "ACHTINÜNIEL",   # ACHTI, NÜNI
    "ZÄNIERBÖUFI",   # ZÄNI, ÖUFI (eleven)
    "ZWÖUFINAUHR",   # ZWÖUFI, UHR
]

# Word positions: (row, start_col, end_col) - inclusive
WORDS = {
    # Always on
    "ES": (0, 0, 1),
    "ISCH": (0, 3, 6),

    # Minute words
    "FÜF": (0, 8, 10),        # 5 minutes
    "ZÄÄ": (1, 8, 10),        # 10 minutes
    "VIERT": (1, 0, 4),       # quarter (15 min)
    "ZWÄNZG": (2, 0, 5),      # 20 minutes

    # Connectors
    "VOR": (2, 8, 10),        # before/to
    "AB": (3, 0, 1),          # after/past
    "HAUBI": (3, 3, 7),       # half

    # Hour words (for "X Uhr" - on the hour)
    "EIS": (4, 0, 2),         # 1
    "ZWÖI": (4, 3, 6),        # 2
    "DRÜ": (4, 8, 10),        # 3
    "VIERI": (5, 0, 4),       # 4
    "FÜFI": (5, 5, 8),        # 5
    "SÄCHSI": (6, 0, 5),      # 6
    "SIBNI": (6, 6, 10),      # 7
    "ACHTI": (7, 0, 4),       # 8
    "NÜNI": (7, 5, 8),        # 9
    "ZÄNI": (8, 0, 3),        # 10
    "ÖUFI": (8, 7, 10),       # 11
    "ZWÖUFI": (9, 0, 5),      # 12

    # O'clock
    "UHR": (9, 8, 10),
}

# Map hour number (1-12) to word key
HOUR_WORDS = {
    1: "EIS",
    2: "ZWÖI",
    3: "DRÜ",
    4: "VIERI",
    5: "FÜFI",
    6: "SÄCHSI",
    7: "SIBNI",
    8: "ACHTI",
    9: "NÜNI",
    10: "ZÄNI",
    11: "ÖUFI",
    12: "ZWÖUFI",
}


def get_words_for_time(hour: int, minute: int) -> list[str]:
    """
    Get the list of words to illuminate for a given time.

    Args:
        hour: Hour in 24h format (0-23)
        minute: Minute (0-59)

    Returns:
        List of word keys to illuminate
    """
    # Convert to 12-hour format
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12

    # Calculate 5-minute interval
    interval = minute // 5

    # Start with "ES ISCH" (always on)
    words = ["ES", "ISCH"]

    # Determine which hour to display
    # For :25-:55, we reference the next hour
    if interval >= 5:  # :25 and later
        display_hour = (hour_12 % 12) + 1
        if display_hour == 0:
            display_hour = 12
    else:
        display_hour = hour_12

    # Add time words based on interval
    if interval == 0:      # :00-:04 → [hour] UHR
        words.append(HOUR_WORDS[hour_12])
        words.append("UHR")
    elif interval == 1:    # :05-:09 → FÜF AB [hour]
        words.extend(["FÜF", "AB", HOUR_WORDS[hour_12]])
    elif interval == 2:    # :10-:14 → ZÄÄ AB [hour]
        words.extend(["ZÄÄ", "AB", HOUR_WORDS[hour_12]])
    elif interval == 3:    # :15-:19 → VIERT AB [hour]
        words.extend(["VIERT", "AB", HOUR_WORDS[hour_12]])
    elif interval == 4:    # :20-:24 → ZWÄNZG AB [hour]
        words.extend(["ZWÄNZG", "AB", HOUR_WORDS[hour_12]])
    elif interval == 5:    # :25-:29 → FÜF VOR HAUBI [next hour]
        words.extend(["FÜF", "VOR", "HAUBI", HOUR_WORDS[display_hour]])
    elif interval == 6:    # :30-:34 → HAUBI [next hour]
        words.extend(["HAUBI", HOUR_WORDS[display_hour]])
    elif interval == 7:    # :35-:39 → FÜF AB HAUBI [next hour]
        words.extend(["FÜF", "AB", "HAUBI", HOUR_WORDS[display_hour]])
    elif interval == 8:    # :40-:44 → ZWÄNZG VOR [next hour]
        words.extend(["ZWÄNZG", "VOR", HOUR_WORDS[display_hour]])
    elif interval == 9:    # :45-:49 → VIERT VOR [next hour]
        words.extend(["VIERT", "VOR", HOUR_WORDS[display_hour]])
    elif interval == 10:   # :50-:54 → ZÄÄ VOR [next hour]
        words.extend(["ZÄÄ", "VOR", HOUR_WORDS[display_hour]])
    elif interval == 11:   # :55-:59 → FÜF VOR [next hour]
        words.extend(["FÜF", "VOR", HOUR_WORDS[display_hour]])

    return words


def get_minute_dots(minute: int) -> int:
    """
    Get the number of corner dots to display (0-4).
    These indicate the exact minute within each 5-minute interval.
    """
    return minute % 5


def get_lit_positions(words: list[str]) -> list[tuple[int, int]]:
    """
    Convert word list to list of (row, col) positions to light up.
    """
    positions = []
    for word in words:
        if word in WORDS:
            row, start, end = WORDS[word]
            for col in range(start, end + 1):
                positions.append((row, col))
    return positions


def print_time_display(hour: int, minute: int):
    """Debug function to print the clock display as ASCII."""
    words = get_words_for_time(hour, minute)
    positions = set(get_lit_positions(words))
    dots = get_minute_dots(minute)

    print(f"\nTime: {hour:02d}:{minute:02d}")
    print(f"Words: {' '.join(words)}")
    print(f"Minute dots: {dots}")
    print()

    # Print corner dots indicator
    dot_str = "●" * dots + "○" * (4 - dots)
    print(f"  {dot_str[0]}         {dot_str[1]}")

    for row_idx, row in enumerate(GRID):
        line = "  "
        for col_idx, char in enumerate(row):
            if (row_idx, col_idx) in positions:
                line += char + " "
            else:
                line += "· "
        print(line)

    print(f"  {dot_str[3]}         {dot_str[2]}")


if __name__ == "__main__":
    # Test various times
    test_times = [
        (7, 0),   # Es isch sibni uhr
        (7, 5),   # Es isch füf ab sibni
        (7, 15),  # Es isch viert ab sibni
        (7, 25),  # Es isch füf vor haubi achti
        (7, 30),  # Es isch haubi achti
        (7, 35),  # Es isch füf ab haubi achti
        (7, 40),  # Es isch zwänzg vor achti
        (7, 47),  # Es isch viert vor achti (+ 2 dots)
        (12, 0),  # Es isch zwöufi uhr
        (0, 0),   # Es isch zwöufi uhr (midnight)
    ]

    for h, m in test_times:
        print_time_display(h, m)
        print("-" * 30)
