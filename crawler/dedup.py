import re
from simhash import Simhash


def clean_text(text: str) -> str:
    """Normalize Chinese text for SimHash comparison."""
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", "", text)
    text = re.sub(r"[0-9]{2}:[0-9]{2}:[0-9]{2}", "", text)
    return text


def compute_simhash(title: str, content: str) -> str:
    """Compute 64-bit SimHash for a news article."""
    text = clean_text(title) + " " + clean_text(content[:500])
    if len(text.strip()) < 20:
        return ""
    return str(Simhash(text).value)


def is_duplicate(hash1: str, hash2: str, threshold: int = 3) -> bool:
    """Check if two hashes represent near-duplicate content."""
    if not hash1 or not hash2:
        return False
    try:
        h1 = int(hash1)
        h2 = int(hash2)
        return Simhash(h1).distance(Simhash(h2)) <= threshold
    except (ValueError, TypeError):
        return False
