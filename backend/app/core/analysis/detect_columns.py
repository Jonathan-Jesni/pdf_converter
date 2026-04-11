def detect_columns(words):
    """
    Detect whether a page has a multi-column layout using gap-based analysis.

    Algorithm:
      1. Collect all word x0 positions and sort them.
      2. Compute gaps between consecutive x0 values.
      3. The largest gap that exceeds GAP_THRESHOLD is a candidate column separator.
      4. Split words into left/right clusters at that boundary.
      5. Validate: each cluster must have enough words, and the right cluster
         must be wide enough to rule out indentation false positives.

    Returns:
        (column_count, column_x_ranges)
        - column_count: 1 or 2
        - column_x_ranges: list of (x_min, x_max) tuples per column
    """
    if not words:
        return 1, []

    # --- Tunables ---
    GAP_THRESHOLD = 50      # minimum gap (pts) to consider a column separator
    MIN_WORDS_PER_COL = 12  # each column must have at least this many words
    MIN_COL_WIDTH = 80      # right column must span at least this many pts

    x_positions = sorted(w["x0"] for w in words)

    if len(x_positions) < 2:
        return 1, [(x_positions[0], x_positions[0])]

    # --- Find the largest gap that exceeds the threshold ---
    best_gap = 0
    best_boundary = None

    for i in range(1, len(x_positions)):
        gap = x_positions[i] - x_positions[i - 1]
        if gap > best_gap:
            best_gap = gap
            best_boundary = (x_positions[i - 1] + x_positions[i]) / 2

    if best_gap < GAP_THRESHOLD or best_boundary is None:
        # No significant gap found — single column
        return 1, [(min(x_positions), max(w["x1"] for w in words))]

    # --- Split words into left / right clusters ---
    left_words = [w for w in words if w["x0"] < best_boundary]
    right_words = [w for w in words if w["x0"] >= best_boundary]

    # --- Validate cluster sizes ---
    if len(left_words) < MIN_WORDS_PER_COL or len(right_words) < MIN_WORDS_PER_COL:
        return 1, [(min(x_positions), max(w["x1"] for w in words))]

    # --- Guard against indentation false-positives ---
    # If the "right column" is very narrow, it's probably indented text,
    # not a real second column.
    right_x0s = [w["x0"] for w in right_words]
    right_x1s = [w["x1"] for w in right_words]
    right_width = max(right_x1s) - min(right_x0s)

    if right_width < MIN_COL_WIDTH:
        return 1, [(min(x_positions), max(w["x1"] for w in words))]

    # --- Build x-range boundaries ---
    left_x_min = min(w["x0"] for w in left_words)
    left_x_max = max(w["x1"] for w in left_words)
    right_x_min = min(right_x0s)
    right_x_max = max(right_x1s)

    return 2, [(left_x_min, left_x_max), (right_x_min, right_x_max)]