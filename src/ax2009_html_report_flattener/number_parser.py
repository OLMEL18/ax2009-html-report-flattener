"""Parsing helpers for Ukrainian/Russian formatted report numbers."""

from __future__ import annotations

import re

_NUMBER_RE = re.compile(r"^\(?-?\d{1,3}(?:[ \u00a0]\d{3})*(?:,\d+)?\)?$|^\(?-?\d+(?:,\d+)?\)?$")


def parse_localized_number(value: str) -> int | float | str:
    """Return a Python number for localized numeric text, or the original text."""
    text = normalize_number_text(value)
    if text == "":
        return ""
    if not _NUMBER_RE.match(text):
        return value

    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()").replace(" ", "").replace("\u00a0", "").replace(",", ".")
    if text.startswith("-"):
        negative = True
        text = text[1:]
    try:
        number = float(text) if "." in text else int(text)
    except ValueError:
        return value
    return -number if negative else number


def normalize_number_text(value: str) -> str:
    return str(value).strip().replace("\u2212", "-")


def looks_numeric(value: str) -> bool:
    return parse_localized_number(value) != value or normalize_number_text(value) in {"0", "0,0", "0,00"}
