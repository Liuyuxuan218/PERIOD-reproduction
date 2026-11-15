#!/usr/bin/env python3
"""Turn the raw PDF extraction into the verified Table 2 PERIOD dataset.

Bug-type rows that sit above a program name were attached to the previous
program by the line cluster. Those four programs are corrected from the
word coordinates on page 9.
"""
import json
import pathlib
import sys

RAW = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
raw = json.loads(RAW.read_text(encoding="utf-8"))

CORRECTIONS = {
    "CB.stringbuffer": {
        "threads": 2,
        "bugs": [{"type": "AF", "depth": 2, "to_bug": 12, "buggy": 16}],
        "schedules": 163,
    },
    "CB.pbzip2": {
        "threads": 4,
        "bugs": [
            {"type": "BOF", "depth": 2, "to_bug": 41, "buggy": 14},
            {"type": "NPD", "depth": 2, "to_bug": 52, "buggy": 41},
            {"type": "UAF", "depth": 1, "to_bug": 53, "buggy": 24},
        ],
        "schedules": 1626,
    },
    "Chess.IWSQ": {
        "threads": 3,
        "bugs": [{"type": "AF", "depth": 3, "to_bug": 108, "buggy": 17}],
        "schedules": 711,
    },
    "Chess.SWSQ": {
        "threads": 3,
        "bugs": [
            {"type": "BOF", "depth": 3, "to_bug": 1628, "buggy": 11},
            {"type": "AF", "depth": 3, "to_bug": 1630, "buggy": 13},
        ],
        "schedules": "L",
    },
    "Chess.IWSQWS": {
        "threads": 3,
        "bugs": [
            {"type": "BOF", "depth": 3, "to_bug": 1661, "buggy": 11},
            {"type": "AF", "depth": 3, "to_bug": 1663, "buggy": 13},
        ],
        "schedules": "L",
    },
}


def cell(value):
    if value in ("L", "%", "-", None, ""):
        return value
    return int(value)


rows = []
for prog in raw["programs"]:
    name = prog["program"]
    if name in CORRECTIONS:
        item = dict(CORRECTIONS[name])
        item["program"] = name
        rows.append(item)
        continue
    shared = prog["shared"]
    rows.append({
        "program": name,
        "threads": cell(shared.get("threads")),
        "bugs": [{
            "type": shared.get("bug_type"),
            "depth": cell(shared.get("bug_depth")),
            "to_bug": cell(shared.get("period_to_bug")),
            "buggy": cell(shared.get("period_buggy")),
        }],
        "schedules": cell(shared.get("period_schedules")),
    })

payload = {
    "source": "ICSE2022_PERIOD.pdf page 9, Table 2, PERIOD columns",
    "markers": {
        "L": "schedule limit reached: 10000, except CS.twostage_100_bad uses 100000",
        "%": "no bug found",
        "-": "bug depth not applicable in the table",
    },
    "programs": rows,
}
OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(len(rows))
