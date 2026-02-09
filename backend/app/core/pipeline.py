def analyze_document(pages):
    profiles = []

    for page_number, page in pages:
        words = page.extract_words(use_text_flow=True)

        from backend.app.core.analysis.build_profile import build_page_profile
        profile = build_page_profile(
            page_number=page_number,
            words=words,
            images=[]
        )

        profiles.append(profile)

    return profiles


def render_document(
    profiles,
    pdf,
    doc,
    renderers
):
    for profile in profiles:
        page = pdf.pages[profile.page_number - 1]
        renderer = renderers.get(profile.detected_mode)

        if renderer:
            renderer(profile, page, doc)

        doc.add_page_break()
