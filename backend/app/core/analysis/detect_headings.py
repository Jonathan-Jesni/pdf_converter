MAX_HEADING_WORDS = 8
SIZE_SCALE = 1.25


def looks_like_heading(text):
    if text.isupper():
        return True

    words = text.split()
    if not words:
        return False

    title_case = sum(1 for w in words if w[0].isupper())
    return title_case >= max(1, len(words) // 2)


def detect_headings(paragraphs, avg_font_size, word_sizes):
    headings = []
    remaining = []

    for i, text in enumerate(paragraphs):
        if not text:
            continue

        words = text.split()
        if len(words) > MAX_HEADING_WORDS:
            remaining.append(text)
            continue

        sizes = word_sizes.get(text)
        if not sizes:
            remaining.append(text)
            continue

        mean_size = sum(sizes) / len(sizes)
        if mean_size < avg_font_size * SIZE_SCALE:
            remaining.append(text)
            continue

        if not looks_like_heading(text):
            remaining.append(text)
            continue

        headings.append(text)

    return headings, remaining
