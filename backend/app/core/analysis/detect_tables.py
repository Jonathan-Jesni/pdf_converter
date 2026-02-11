MIN_COL_REPEAT = 4
ROW_Y_THRESHOLD = 8
COL_X_THRESHOLD = 15
MIN_ROWS = 3
MIN_COLS = 2
MIN_MULTI_CELL_ROWS_RATIO = 0.6


def detect_tables(profile):
    words = profile.words
    if not words:
        return

    # ---- Group words into rows ----
    rows = []
    current = []

    for w in sorted(words, key=lambda x: (x["top"], x["x0"])):
        if not current:
            current.append(w)
            continue

        if abs(w["top"] - current[-1]["top"]) <= ROW_Y_THRESHOLD:
            current.append(w)
        else:
            rows.append(current)
            current = [w]

    if current:
        rows.append(current)

    if len(rows) < MIN_ROWS:
        return

    # ---- Count repeated x positions across rows ----
    col_counts = {}

    for row in rows:
        seen_in_row = set()
        for w in row:
            x = w["x0"]

            matched = False
            for cx in list(col_counts.keys()):
                if abs(x - cx) <= COL_X_THRESHOLD:
                    if cx not in seen_in_row:
                        col_counts[cx] += 1
                        seen_in_row.add(cx)
                    matched = True
                    break

            if not matched:
                col_counts[x] = 1
                seen_in_row.add(x)

    columns = [
        cx for cx, count in col_counts.items()
        if count >= MIN_COL_REPEAT
    ]

    if len(columns) < 3:
        return

    columns.sort()

    # ---- Reject wide two-column layout (likely layout, not table) ----
    if len(columns) == 2:
        column_gap = abs(columns[1] - columns[0])
        if column_gap > 200:   # adjust if needed
            return


    # ---- Check how many rows actually have multiple column hits ----
    multi_cell_rows = 0

    for row in rows:
        hits = 0
        for w in row:
            for cx in columns:
                if abs(w["x0"] - cx) <= COL_X_THRESHOLD:
                    hits += 1
                    break
        if hits >= 3:
            multi_cell_rows += 1

    if multi_cell_rows / len(rows) < MIN_MULTI_CELL_ROWS_RATIO:
        return

    # ---- Build grid ----
    grid = []

    for row in rows:
        cells = [""] * len(columns)
        for w in row:
            for i, cx in enumerate(columns):
                if abs(w["x0"] - cx) <= COL_X_THRESHOLD:
                    cells[i] += w["text"] + " "
                    break
        grid.append([c.strip() for c in cells])
    
    # ---- Reject if row widths vary too much (likely layout) ----
    row_widths = []

    for row in rows:
        if not row:
            continue
        min_x = min(w["x0"] for w in row)
        max_x = max(w["x1"] for w in row)
        row_widths.append(max_x - min_x)

    if not row_widths:
        return

    avg_width = sum(row_widths) / len(row_widths)
    width_variation = max(row_widths) - min(row_widths)

    # If rows have very inconsistent widths, it's likely layout text
    if width_variation > avg_width * 0.6:
        return


    profile.has_table_grid = True
    profile.table_cells = grid
