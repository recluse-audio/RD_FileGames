"""
sync_rumor_csv.py
-----------------
Reads Secret_x_Rumor.csv (source of truth) and updates the Secret column in
Rumor.csv to match, preserving all other columns (Summary, test scores, etc.)
that have been filled in manually.

Run any time either CSV changes:
    python sync_rumor_csv.py
"""

import csv
import os
import re

HERE             = os.path.dirname(os.path.abspath(__file__))
SECRET_CSV_PATH  = os.path.join(HERE, "Secret_x_Rumor.csv")
RUMOR_CSV_PATH   = os.path.join(HERE, "Rumor.csv")


def normalise_contestant(name: str) -> str:
    """Lower-case and strip so 'Bernard' and 'Bernie' both key on 'bernard'/'bernie'."""
    return name.strip().lower()


def rumor_scene_to_key(rumor_scene: str) -> tuple[str, int] | None:
    """
    Turn 'Jean_Rumor_2' or 'Bernie_Rumor_1' into ('jean', 2).
    Returns None if the pattern doesn't match.
    """
    m = re.match(r"([A-Za-z]+)_Rumor_(\d+)", rumor_scene.strip(), re.IGNORECASE)
    if not m:
        return None
    contestant = m.group(1).lower()
    # Treat 'bernie' and 'bernard' as the same character
    if contestant == "bernie":
        contestant = "bernard"
    return contestant, int(m.group(2))


def rumor_row_to_key(contestant: str, rumor_col: str) -> tuple[str, int] | None:
    """
    Turn Rumor.csv row ('Jean', 'Rumor 2:') into ('jean', 2).
    Returns None if the pattern doesn't match.
    """
    m = re.search(r"(\d+)", rumor_col)
    if not m:
        return None
    contestant_norm = normalise_contestant(contestant)
    if contestant_norm == "bernie":
        contestant_norm = "bernard"
    return contestant_norm, int(m.group(1))


def cell(row: list[str], idx: int) -> str:
    """Safe indexed access into a csv.reader row."""
    return row[idx].strip() if idx < len(row) else ""


# ------------------------------------------------------------------
# 1. Build reverse map: (contestant, rumor_number) -> secret label
# ------------------------------------------------------------------
# Secret_x_Rumor.csv has a duplicate "Contestant" column header, so read
# by column index to avoid DictReader clobbering the first value.
#   col 0 = Contestant, col 1 = Secret, col 2 = Summary, col 3 = Rumor
reverse: dict[tuple[str, int], str] = {}

with open(SECRET_CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        contestant  = cell(row, 0)
        secret      = cell(row, 1)
        rumor_scene = cell(row, 3)
        if not contestant or not secret or not rumor_scene:
            continue
        key = rumor_scene_to_key(rumor_scene)
        if key is None:
            continue
        if key in reverse:
            print(f"  Warning: duplicate mapping for {key} — keeping first ({reverse[key]}), ignoring ({secret})")
            continue
        # Prefix with the owning contestant name so it's clear whose secret it is
        reverse[key] = f"{contestant} {secret}"

# ------------------------------------------------------------------
# 2. Read Rumor.csv, update Secret column, write back
# ------------------------------------------------------------------
with open(RUMOR_CSV_PATH, newline="", encoding="utf-8") as f:
    reader     = csv.DictReader(f)
    fieldnames = reader.fieldnames or []
    rows       = list(reader)

updated = 0
for row in rows:
    contestant = (row.get("Contestant") or "").strip()
    rumor_col  = (row.get("Rumor")      or "").strip()
    if not contestant or not rumor_col:
        continue
    key = rumor_row_to_key(contestant, rumor_col)
    if key is None:
        continue
    new_secret = reverse.get(key, "")
    if (row.get("Secret") or "").strip() != new_secret:
        row["Secret"] = new_secret
        updated += 1

with open(RUMOR_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done — {updated} Secret cell(s) updated in Rumor.csv")
