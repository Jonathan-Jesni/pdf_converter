def detect_columns(words):
    if not words:
        return 1, []

    x_positions = [w["x0"] for w in words]
    spread = max(x_positions) - min(x_positions)

    if spread > 300:
        mid = sorted(x_positions)[len(x_positions) // 2]
        return 2, [(0, mid), (mid, max(x_positions))]

    return 1, [(min(x_positions), max(x_positions))]
