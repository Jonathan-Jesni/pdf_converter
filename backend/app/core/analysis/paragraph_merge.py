PARAGRAPH_GAP_THRESHOLD = 12
LINE_END_PUNCT = (".", "?", "!", ":")


def merge_lines_into_paragraphs(lines):
    paragraphs = []
    current = []

    last_top = None

    for top, text in lines:
        if not text:
            continue

        if (
            last_top is not None
            and abs(top - last_top) > PARAGRAPH_GAP_THRESHOLD
            and current
        ):
            paragraphs.append(" ".join(current).strip())
            current = []

        if current:
            prev = current[-1]
            if (
                not prev.endswith(LINE_END_PUNCT)
                and not text[0].isupper()
            ):
                current[-1] = prev + " " + text
            else:
                current.append(text)
        else:
            current.append(text)

        last_top = top

    if current:
        paragraphs.append(" ".join(current).strip())

    return paragraphs
