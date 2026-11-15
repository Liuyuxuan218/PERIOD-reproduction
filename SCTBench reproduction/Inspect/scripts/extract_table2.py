#!/usr/bin/env python3
"""Rebuild Table 2 PERIOD columns from the paper PDF word positions."""
import json
import sys

import pymupdf

PDF = sys.argv[1]
OUT = sys.argv[2]

# Column centers measured from page 9 header glyphs.
COLUMNS = [
    ("threads", 135.7),
    ("bug_type", 158.2),
    ("bug_depth", 178.0),
    ("period_to_bug", 197.0),
    ("period_schedules", 213.5),
    ("period_buggy", 228.8),
]


def nearest(x):
    name, _center = min(COLUMNS, key=lambda item: abs(item[1] - x))
    if abs(dict(COLUMNS)[name] - x) > 12:
        return None
    return name


def main():
    doc = pymupdf.open(PDF)
    page = doc[8]
    words = []
    for w in page.get_text("words"):
        x0, y0, x1, y1, text = w[:5]
        if 160 <= y0 <= 500:
            words.append((y0, (x0 + x1) / 2, text))
    lines = []
    for y, x, text in words:
        if lines and abs(lines[-1][0] - y) < 2.4:
            lines[-1][1].append((x, text))
        else:
            lines.append([y, [(x, text)]])
    programs = []
    current = None
    for y, items in lines:
        items.sort()
        name = " ".join(t for x, t in items if x < 120).strip()
        buckets = {key: [] for key, _ in COLUMNS}
        for x, text in items:
            if x < 120:
                continue
            col = nearest(x)
            if col:
                buckets[col].append(text)
        if name.startswith(("CS.", "CB.", "Chess.", "Inspect.", "Misc.", "Splash2.", "RADBench.")):
            current = {"program": name, "y": round(y, 2), "rows": []}
            programs.append(current)
            current["shared"] = {key: " ".join(vals) for key, vals in buckets.items() if vals}
        elif current is not None:
            current["rows"].append({key: " ".join(vals) for key, vals in buckets.items() if vals})
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"page": 9, "programs": programs}, fh, indent=2)
        fh.write("\n")
    print("programs", len(programs))


if __name__ == "__main__":
    main()
