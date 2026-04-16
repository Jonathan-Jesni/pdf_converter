from .page_profile import PageProfile
from .detect_columns import detect_columns
from .paragraph_merge import merge_lines_into_paragraphs
from .detect_lists import detect_lists
from .detect_headings import detect_headings
from .detect_tables import detect_tables


def build_page_profile(page_number, words, images):
    profile = PageProfile(page_number=page_number)
    profile.words = words
    profile.images = images

    profile.columns, profile.column_x_ranges = detect_columns(words)

    if words:
        profile.text_density = len(words)

        sizes = [w["size"] for w in words if "size" in w]
        profile.avg_font_size = sum(sizes) / len(sizes) if sizes else 0.0

        from collections import defaultdict

        line_map = defaultdict(list)

        for w in words:
            if "top" in w and "text" in w:
                line_map[round(w["top"] / 10) * 10].append(w["text"])

        lines = [
            (top, " ".join(texts))
            for top, texts in sorted(line_map.items())
        ]

        profile.paragraphs = merge_lines_into_paragraphs(lines)

        profile.lists, profile.paragraphs = detect_lists(profile.paragraphs)

        word_sizes = {}
        for w in words:
            if "text" in w and "size" in w:
                word_sizes.setdefault(w["text"], []).append(w["size"])

        profile.headings, profile.paragraphs = detect_headings(
            profile.paragraphs,
            profile.avg_font_size,
            word_sizes
        )

    detect_tables(profile)
    profile.decide_mode()
    return profile
