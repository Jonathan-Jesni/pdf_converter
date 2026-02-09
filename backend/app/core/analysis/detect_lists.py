import re

BULLET_RE = re.compile(r"^\s*([•\-–*])\s+(.*)")
NUMBER_RE = re.compile(r"^\s*((\d+[\.\)])|(\(\d+\))|([a-z]\)))\s+(.*)")


def detect_lists(paragraphs):
    lists = []
    remaining = []

    current = []
    current_type = None

    def flush():
        nonlocal current, current_type
        if len(current) >= 2:
            lists.append(current)
        else:
            remaining.extend(current)
        current = []
        current_type = None

    for p in paragraphs:
        m_b = BULLET_RE.match(p)
        m_n = NUMBER_RE.match(p)

        if m_b:
            if current_type not in (None, "bullet"):
                flush()
            current_type = "bullet"
            current.append(m_b.group(2).strip())
            continue

        if m_n:
            if current_type not in (None, "number"):
                flush()
            current_type = "number"
            current.append(m_n.group(len(m_n.groups())).strip())
            continue

        flush()
        remaining.append(p)

    flush()
    return lists, remaining
