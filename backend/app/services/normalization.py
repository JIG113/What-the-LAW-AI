import re


def normalize_korean_public_notice_text(text: str) -> str:
    t = text.replace("\u00a0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)

    replacements = {
        "m2": "㎡",
        "제 출": "제출",
        "심 의": "심의",
        "사 업": "사업",
    }
    for src, dst in replacements.items():
        t = t.replace(src, dst)

    return t.strip()
