# Keyset pagination. The cursor is the last sort key, not a skip count.
# Index required for the database form: (civic_id) or (updated_at, civic_id).

from __future__ import annotations


def keyset_page(rows, cursor=None, size=20, key=lambda row: row["civic_id"]):
    """Return the next page strictly after cursor. rows must already be ordered by key."""
    size = max(1, int(size))
    rest = rows if cursor is None else [row for row in rows if key(row) > cursor]
    page = rest[:size]
    nxt = key(page[-1]) if len(rest) > size else None
    return {
        "page": page,
        "cursor": key(page[-1]) if page else cursor,
        "next_cursor": nxt,
        "has_more": nxt is not None,
        "start": key(page[0]) if page else None,
    }


def previous_cursor(rows, first_key, size=20, key=lambda row: row["civic_id"]):
    """Cursor that opens the page ending just before first_key."""
    before = [row for row in rows if key(row) < first_key]
    if not before:
        return None
    start = max(0, len(before) - max(1, int(size)))
    prev = before[start:]
    index = next(i for i, row in enumerate(rows) if key(row) == key(prev[0]))
    return None if index == 0 else key(rows[index - 1])


if __name__ == "__main__":
    citizens = [
        {"civic_id": 1, "citizen": "Carrier"},
        {"civic_id": 2, "citizen": "Casimir spectrum"},
        {"civic_id": 3, "citizen": "Kernel operator"},
        {"civic_id": 4, "citizen": "Decomposition"},
        {"civic_id": 5, "citizen": "Dimension 47"},
    ]
    cursor = None
    while True:
        result = keyset_page(citizens, cursor, 2)
        print([row["civic_id"] for row in result["page"]])
        if not result["has_more"]:
            break
        cursor = result["next_cursor"]
