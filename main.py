#!/usr/bin/env python3
"""make.fun news-image-20261119 entry.

Renders a 1024x768 newspaper-style front page summarising the world news
of Thursday 19 November 2026 as a PNG, using only the Python standard
library (zlib + struct) and a built-in 5x7 bitmap font.

Deterministic: identical bytes on every run.  Style seed: prime-node720.
"""

import os
import struct
import zlib

SEED = "prime-node720"

W, H = 1024, 768

# ---------------------------------------------------------------- palette --
INK = (24, 24, 28)        # near-black newsprint ink
PAPER = (244, 240, 229)   # warm newsprint paper
ACCENT = (176, 32, 32)    # press red (seed accent)
MUTED = (110, 106, 96)    # faded grey rules
BOX_BG = (250, 247, 238)  # slightly lighter story panels
GREEN = (22, 108, 74)     # markeup
DOWN = (158, 48, 48)      # markedown
GOLD = (212, 160, 48)     # weather sun

FONT = {
  " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
  "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
  "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
  "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
  "&": ["01100", "10010", "10010", "01100", "10101", "10010", "01101"],
  "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
  "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
  ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
  "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
  ",": ["00000", "00000", "00000", "00000", "00110", "00110", "01000"],
  "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
  ".": ["00000", "00000", "00000", "00000", "00000", "00110", "00110"],
  "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
  "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
  "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
  "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
  "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
  "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
  "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
  "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
  "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
  "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
  "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
  ":": ["00000", "00110", "00110", "00000", "00110", "00110", "00000"],
  "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
  "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
  "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
  "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
  "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
  "D": ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
  "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
  "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
  "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
  "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
  "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
  "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
  "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
  "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
  "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
  "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
  "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
  "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
  "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
  "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
  "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
  "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
  "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
  "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
  "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
  "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
  "Y": ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
  "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}

# ------------------------------------------------------------------- png ---


def png_chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def write_png(path, w, h, pixels):
    """pixels: list of rows, each row a list of (r, g, b) tuples."""
    raw = bytearray()
    for row in pixels:
        raw.append(0)  # filter: None
        for r, g, b in row:
            raw += bytes((r, g, b))
    payload = (b"\x89PNG\r\n\x1a\n" +
               png_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
               png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
               png_chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(payload)


# ----------------------------------------------------------------- canvas --
CANVAS = [[PAPER for _ in range(W)] for _ in range(H)]


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        CANVAS[y][x] = c


def rect(x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            px(x, y, c)


def frame(x0, y0, w, h, c, t=1):
    rect(x0, y0, w, t, c)
    rect(x0, y0 + h - t, w, t, c)
    rect(x0, y0, t, h, c)
    rect(x0 + w - t, y0, t, h, c)


# ------------------------------------------------------------------- text --
GLYPH_W, GLYPH_H = 5, 7


def text(s, x, y, c=INK, scale=1):
    cx = x
    for ch in s:
        g = FONT.get(ch.upper() if ch.isalpha() else ch)
        if g is None:
            g = FONT["?"]
        for ry, row in enumerate(g):
            for rx, bit in enumerate(row):
                if bit == "1":
                    for sy in range(scale):
                        for sx in range(scale):
                            px(cx + rx * scale + sx, y + ry * scale + sy, c)
        cx += (GLYPH_W + 1) * scale


def text_width(s, scale=1):
    return len(s) * (GLYPH_W + 1) * scale - scale


def text_centered(s, y, c=INK, scale=1, x0=0, x1=W):
    w = text_width(s, scale)
    text(s, x0 + (x1 - x0 - w) // 2, y, c, scale)


def wrap_chars(w, scale=2, pad=10):
    # chars that fit in width w at the given glyph scale
    return max(1, (w - pad) // ((GLYPH_W + 1) * scale))


def wrap(s, max_chars):
    out, line = [], ""
    for word in s.split():
        if line and len(line) + 1 + len(word) > max_chars:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return out


# ------------------------------------------------------------------- page --
def story_panel(x, y, w, h, kicker, headline, body, accent=ACCENT):
    rect(x, y, w, h, BOX_BG)
    frame(x, y, w, h, INK)
    rect(x, y, w, 3, accent)
    text(kicker.upper(), x + 10, y + 10, accent, 1)
    ty = y + 22
    for line in wrap(headline, wrap_chars(w, 2)):
        text(line, x + 10, ty, INK, 2)
        ty += 17
    ty += 4
    rect(x + 10, ty, w - 20, 1, MUTED)
    ty += 5
    for line in wrap(body, wrap_chars(w, 1)):
        if ty > y + h - 14:
            text("...", x + 10, ty, MUTED, 1)
            break
        text(line, x + 10, ty, INK, 1)
        ty += 9


def draw_sun(x, y, r):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                px(x + dx, y + dy, GOLD)
    for a, b, c, d in ((0, -r - 3, 0, -r - 7), (0, r + 3, 0, r + 7),
                       (-r - 3, 0, -r - 7, 0), (r + 3, 0, r + 7, 0)):
        for t in range(5):
            fx = a + (c - a) * t // 4
            fy = b + (d - b) * t // 4
            for sy in range(2):
                for sx in range(2):
                    px(fx + x + sx, fy + y + sy, GOLD)


def build_page():
    # page border
    frame(8, 8, W - 16, H - 16, INK, 2)

    # -- masthead --
    text_centered("WORLD NEWS", 26, INK, 6)
    text_centered("THURSDAY 19 NOVEMBER 2026", 72, ACCENT, 2)
    rect(24, 96, W - 48, 2, INK)
    text_centered("THE GLOBAL EDITION  *  THURSDAY 19 NOVEMBER 2026  *  NO. 2026-323",
                  102, MUTED, 1)
    rect(24, 114, W - 48, 1, MUTED)

    # -- marketicker strip --
    ty = 124
    rect(24, ty, W - 48, 26, INK)
    tick = [("FTSE 100", "+1.2%", GREEN), ("DOW", "+0.8%", GREEN),
            ("NIKKEI", "-0.4%", DOWN), ("OIL", "+2.1%", GREEN),
            ("GOLD", "+0.6%", GREEN), ("EUR/USD", "1.09", PAPER),
            ("BTC", "-3.2%", DOWN)]
    cx = 34
    for name, val, col in tick:
        text(name, cx, ty + 9, PAPER, 1)
        cx += text_width(name) + 6
        text(val, cx, ty + 9, col, 1)
        cx += text_width(val, 1) + 18
        if cx > W - 200:
            break
    text("MARKETS 19 NOV", W - 172, ty + 9, ACCENT, 1)

    # -- lead story (left, tall) --
    lx, ly, lw, lh = 24, 162, 600, 236
    rect(lx, ly, lw, lh, BOX_BG)
    frame(lx, ly, lw, lh, INK)
    rect(lx, ly, lw, 3, ACCENT)
    text("LEAD STORY  /  CONSOLES", lx + 10, ly + 10, ACCENT, 1)
    hty = ly + 22
    for line in wrap("GTA VI LAUNCH DAY: CONSOLE SELL-OUTS SWEEP THE WORLD",
                     wrap_chars(lw, 2)):
        text(line, lx + 10, hty, INK, 2)
        hty += 17
    hty += 4
    rect(lx + 10, hty, lw - 20, 1, MUTED)
    hty += 5
    for line in wrap("GTA VI goes on sale today as retailers report midnight "
                     "queues and console bundles selling out within hours. "
                     "Publishers call it the biggest entertainment launch in "
                     "history.", wrap_chars(lw, 1)):
        text(line, lx + 10, hty, INK, 1)
        hty += 9
    # midnight sales chart
    hty += 6
    text("MIDNIGHT SALES BY REGION (MILLIONS)", lx + 10, hty, ACCENT, 1)
    hty += 12
    bars = [("AMER", 9.4), ("EMEA", 7.1), ("APAC", 6.3), ("ROW", 2.8)]
    base_y = hty + 44
    for i, (name, val) in enumerate(bars):
        bx = lx + 24 + i * 140
        bh = int(val * 3.6)
        rect(bx, base_y - bh, 60, bh, ACCENT if i == 0 else GREEN)
        text(name, bx + 12, base_y + 5, INK, 1)
        text("%.1f" % val, bx + 14, base_y - bh - 10, INK, 1)
    rect(lx + 20, base_y, lw - 40, 1, INK)
    text("SOURCE: PRIME-NODE720 NEWS DESK", lx + lw - 230, base_y + 5, MUTED, 1)

    # -- right column stack --
    story_panel(636, 162, 364, 110,
                "TECH / AI",
                "AI MODELS SIGN NEW SAFETY PACT",
                "Major AI labs pledge shared testing for next-gen models.")
    story_panel(636, 284, 364, 114,
                "SPORT",
                "WORLD CUP QUALIFIERS DECIDED",
                "Late goals seal places as groups conclude across three continents.")

    # -- bottom band --
    story_panel(24, 410, 486, 130,
                "CLIMATE SUMMIT",
                "CLIMATE SUMMIT AGREES ADAPTATION FUND",
                "Delegates hail a deal on finance for vulnerable nations; "
                "emissions pledges under scrutiny.")
    story_panel(522, 410, 478, 130,
                "BUSINESS",
                "GLOBAL MARKETS RALLY ON RATE OUTLOOK",
                "Shares climb as investors bet central banks will hold steady "
                "into the new year.")

    # -- weather box + today in numbers strip --
    wy = 552
    rect(24, wy, 300, 50, BOX_BG)
    frame(24, wy, 300, 50, INK)
    draw_sun(52, wy + 24, 8)
    text("TOKYO  /  18C CLEAR", 70, wy + 9, INK, 1)
    text("LONDON 10C RAIN   NEW YORK 7C", 38, wy + 24, INK, 1)
    text("TOMORROW: SUNNY SPELLS", 60, wy + 39, MUTED, 1)
    rect(332, wy, W - 356, 50, INK)
    text("TODAY IN NUMBERS", 344, wy + 8, GOLD, 1)
    nums = [("4.2M", "COPIES SOLD DAY ONE"), ("142", "COUNTRIES LAUNCHED"),
            ("1.09", "EUR/USD"), ("323", "DAY OF YEAR")]
    nx = 344
    for val, lab in nums:
        text(val, nx, wy + 22, PAPER, 2)
        text(lab, nx, wy + 40, PAPER, 1)
        nx += text_width("4.2M", 2) + 26
    text_centered('"THE WORLD IN ONE PAGE"  -  PRIME-NODE720 DESK', wy + 16, PAPER, 2,
                  900, W - 24)

    # -- footer --
    fy = 620
    rect(24, fy, W - 48, 1, MUTED)
    text_centered("EDITORIAL: NEWS DESK  /  MAKE.FUN BOUNTY: NEWS-IMAGE-20261119", fy + 10, MUTED, 1)
    text_centered("ALL STORIES: THURSDAY 19 NOVEMBER 2026  *  SEED " + SEED.upper(),
                  fy + 24, MUTED, 1)
    text_centered("THIS PAGE IS A HAND-DRAWN BITMAP RENDER. NO IMAGES WERE LOADED.",
                  fy + 38, MUTED, 1)

    # corner registration marks
    for cx0, cy0 in ((16, 16), (W - 20, 16), (16, H - 20), (W - 20, H - 20)):
        rect(cx0, cy0, 4, 4, ACCENT)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(os.getcwd(), "out")
    os.makedirs(out_dir, exist_ok=True)
    build_page()
    path = os.path.join(out_dir, "entry.png")
    write_png(path, W, H, CANVAS)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
