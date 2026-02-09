from .page_profile import PageProfile
from .detect_columns import detect_columns

def build_page_profile(page_number, words, images):
    profile = PageProfile(page_number=page_number)
    profile.words = words
    profile.images = images

    profile.columns, profile.column_x_ranges = detect_columns(words)

    if words:
        profile.text_density = len(words)
        sizes = [w["size"] for w in words if "size" in w]
        profile.avg_font_size = sum(sizes) / len(sizes) if sizes else 0.0

    profile.decide_mode()
    return profile
