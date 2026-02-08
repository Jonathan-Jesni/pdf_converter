def detect_mode(text_blocks, page_width):
    if not text_blocks:
        return "semantic", "no text blocks detected"

    x0_norm = [b[0] / page_width for b in text_blocks]
    x1_norm = [b[2] / page_width for b in text_blocks]

    # ---- Column detection ----
    xs = sorted(x0_norm)
    clusters = []
    current = [xs[0]]

    for x in xs[1:]:
        if abs(x - current[-1]) <= 0.15:
            current.append(x)
        else:
            clusters.append(current)
            current = [x]

    clusters.append(current)
    column_count = sum(1 for c in clusters if len(c) >= 2)

    # ---- Form alignment detection ----
    left_freq = {}
    right_freq = {}

    for x0, x1 in zip(x0_norm, x1_norm):
        lx = round(x0, 2)
        rx = round(x1, 2)
        left_freq[lx] = left_freq.get(lx, 0) + 1
        right_freq[rx] = right_freq.get(rx, 0) + 1

    max_left = max(left_freq.values(), default=0)
    max_right = max(right_freq.values(), default=0)

    form_detected = max_left >= 4 and max_right >= 4

    # ---- Decision ----
    if form_detected:
        return "form", "consistent left-right alignment detected"
    elif column_count >= 2:
        return "layout", f"{column_count} distinct columns detected"
    else:
        return "semantic", "single continuous text flow"
