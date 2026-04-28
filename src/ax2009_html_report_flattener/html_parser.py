"""HTML table extraction for Dynamics-style exported reports."""

from __future__ import annotations

from dataclasses import dataclass
import re

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class HtmlCell:
    text: str
    colspan: int = 1
    font_weight: str = ""
    text_align: str = ""
    border: str = ""


@dataclass(frozen=True)
class HtmlRow:
    cells: tuple[HtmlCell, ...]

    @property
    def texts(self) -> list[str]:
        expanded: list[str] = []
        for cell in self.cells:
            expanded.append(cell.text)
            expanded.extend([""] * (max(cell.colspan, 1) - 1))
        return expanded


_SPACE_RE = re.compile(r"\s+")


def parse_html_tables(html: str) -> list[HtmlRow]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[HtmlRow] = []
    for tr in soup.find_all("tr"):
        cells: list[HtmlCell] = []
        for tag in tr.find_all(["td", "th"], recursive=False):
            colspan = _safe_int(tag.get("colspan"), default=1)
            style = str(tag.get("style", ""))
            text = normalize_cell_text(tag.get_text(" ", strip=True))
            if _is_zero_width(style) and not text:
                continue
            cells.append(
                HtmlCell(
                    text=text,
                    colspan=max(colspan, 1),
                    font_weight=_style_value(style, "font-weight"),
                    text_align=_style_value(style, "text-align"),
                    border=_style_value(style, "border"),
                )
            )
        if cells:
            rows.append(HtmlRow(tuple(cells)))
    return rows


def normalize_cell_text(value: str) -> str:
    return _SPACE_RE.sub(" ", value.replace("\xa0", " ")).strip()


def _safe_int(value: object, default: int) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _style_value(style: str, name: str) -> str:
    for part in style.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        if key.strip().lower() == name:
            return value.strip().lower()
    return ""


def _is_zero_width(style: str) -> bool:
    return "width:0" in style.replace(" ", "").lower()
