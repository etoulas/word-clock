# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bernese German (Bärndütsch) word clock for a 64x64 RGB LED matrix panel. Displays time in 5-minute intervals as written words, inspired by QLOCKTWO. Four corner dots indicate exact minutes within each interval.

**Hardware**: Seengreat RGB Matrix P3.0 64x64 (HUB75 interface) on Raspberry Pi

## Commands

```bash
# Run on Raspberry Pi (requires sudo for GPIO)
sudo python3 clock.py

# Run in simulation mode (terminal output, no hardware)
python3 clock.py --simulate

# Run tests
python3 test_clock.py

# Visual demo of all time intervals
python3 test_clock.py --demo

# Install on Raspberry Pi
sudo ./install.sh
```

## Architecture

```
word_grid.py   - Bernese German 11x10 character grid and time-to-words logic
display.py     - Maps character grid positions to 64x64 pixel coordinates
clock.py       - Main application loop, handles hardware and CLI options
```

**Time Logic**: `get_words_for_time(hour, minute)` returns word keys. `get_lit_positions(words)` converts to (row, col) grid positions. The display renderer then maps these to pixel coordinates on the LED panel.

**Word Grid**: 11 columns x 10 rows. Each word has a position tuple `(row, start_col, end_col)` in the `WORDS` dict. Characters are rendered as 5x5 pixel blocks with 1px spacing.

## Bernese German Time Format

- `:00` → ES ISCH [hour] UHR
- `:05` → ES ISCH FÜF AB [hour]
- `:25` → ES ISCH FÜF VOR HAUBI [next hour]
- `:30` → ES ISCH HAUBI [next hour]
- `:35` → ES ISCH FÜF AB HAUBI [next hour]
- `:40` → ES ISCH ZWÄNZG VOR [next hour]

Corner dots (0-4) show `minute % 5`.
