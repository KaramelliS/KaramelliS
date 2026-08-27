"""Palette, type stack and shared SVG chrome for every profile asset.

Two themes, generated from one definition, because a GitHub reader may be on
either. The names are paper/ink rather than light/dark: the light theme is warm
stock, not white, and the dark theme keeps that warmth in its foreground so the
pair reads as one object photographed under two lights.
"""

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(
        bg="#f2eee4",        # warm stock
        inset="#e8e3d6",     # recessed panel
        ink="#14110c",
        ink2="#4b4539",
        ink3="#726a58",
        rule="#cdc6b4",
        rule2="#dfd9c9",
        accent="#b23c0c",    # annotation vermilion
        accent2="#0d5f68",   # secondary field class
        heat=["#e2ddcd", "#e8c9a4", "#dd9a5b", "#c4651f", "#8f3a06"],
        void="#eae5d8",      # days before the account existed
        wordmark="#14110c",
        # Sequential ramp for the language map, ordered largest to smallest.
        # One warm family rather than GitHub's per-language colours: twelve
        # unrelated hues would be the loudest thing on the page and would say
        # nothing that the ordering does not already say.
        ramp=["#8f2f06", "#b23c0c", "#c76a22", "#d69a52", "#c2ab80", "#a89e86"],
        tail="#b8b09c",
    ),
    "dark": dict(
        bg="#101318",
        inset="#171b21",
        ink="#ece7db",
        ink2="#a9a294",
        ink3="#8a8172",
        rule="#2a303a",
        rule2="#20262e",
        accent="#ff7038",
        accent2="#59cfdd",
        heat=["#1c2129", "#4a2c17", "#8a4c1c", "#cf7226", "#ff9a52"],
        void="#14171c",
        wordmark="#ece7db",
        ramp=["#ff8a52", "#f46c30", "#cf7833", "#a67a48", "#7d735b", "#5f5a4b"],
        tail="#4a4740",
    ),
}


def rel_lum(hexstr):
    c = [int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def on(bg_hex, theme):
    """Foreground for text sitting on `bg_hex`: whichever of the theme's ink and
    its page colour reads better against it. Cell fills in the calendar run the
    whole ramp, so the digits cannot pick one colour and hope."""
    return theme["ink"] if contrast(theme["ink"], bg_hex) >= contrast(theme["bg"], bg_hex) else theme["bg"]
