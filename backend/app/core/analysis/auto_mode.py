def detect_mode(profile, page_width):
    words = profile.words

    if not words:
        profile.reason = "no text blocks detected"
        return

    text_blocks = [
        (w["x0"], w["top"], w["x1"], w["bottom"])
        for w in words
        if "x0" in w and "x1" in w and "top" in w and "bottom" in w
    ]

    if not text_blocks:
        profile.reason = "no usable text geometry"
        return

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

    if column_count >= 2:
        profile.columns = column_count

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

    if max_left >= 4 and max_right >= 4:
        profile.has_form_alignment = True
        profile.reason = "consistent left-right alignment detected"
        return

    if column_count >= 2:
        profile.reason = f"{column_count} distinct columns detected"
        return

    profile.reason = "single continuous text flow"
