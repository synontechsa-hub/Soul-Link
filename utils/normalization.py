# utils/normalization.py
from typing import Any, List

def normalize_list(value: Any) -> List[str]:
    """
    Normalize JSON fields into a list of strings.

    Accepts:
    - list → returned as-is
    - string → split on commas or slashes
    - None / invalid → empty list
    """
    if not value:
        return []

    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]

    if isinstance(value, str):
        parts = value.replace("/", ",").split(",")
        return [p.strip().strip('"') for p in parts if p.strip()]

    return []
