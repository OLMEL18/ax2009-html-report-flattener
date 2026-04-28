"""Flatten Dynamics-style HTML report tables into records."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from .html_parser import HtmlRow, parse_html_tables
from .number_parser import looks_numeric, parse_localized_number


SKIP_KEYWORDS = (
    "Страница",
    "Page",
    "В соответствии с",
    "Общий итог",
    "Окончательный общий итог",
    "Итого",
    "Всего",
    "Разом",
    "Total",
    "Grand total",
    "Данные о затратах",
)

HEADER_HINTS = {
    "Код номенклатуры",
    "Наименование номенклатуры",
    "Склад",
    "Количество",
    "Сумма затрат",
    "Номенклатурная группа",
    "Значение",
    "Счет поставщика",
    "Имя",
    "Операция",
    "Дата",
    "Текст проводки",
    "Дебет",
    "Кредит",
    "Валюта",
    "Сумма в валюте",
    "Счет",
    "Код",
    "Наименование",
    "Сальдо на начало периода",
    "Обороты за период",
    "Сальдо на конец периода",
    "Счет ГК",
    "Документ",
}

CONTEXT_FIELDS = (
    "Счет поставщика",
    "Имя",
    "Счет ГК",
    "Код",
    "Наименование",
    "Номенклатурная группа",
)

NUMERIC_HEADER_WORDS = (
    "Количество",
    "Сумма",
    "Значение",
    "Дебет",
    "Кредит",
    "Сальдо",
    "Обороты",
)


@dataclass
class ConversionStats:
    input_file: str = ""
    output_file: str = ""
    html_rows_read: int = 0
    exported_rows: int = 0
    skipped_rows: int = 0
    detected_headers: list[list[str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class FlatTable:
    headers: list[str]
    rows: list[dict[str, object]]
    stats: ConversionStats


def convert_html_to_flat_table(input_path: str | Path) -> FlatTable:
    path = Path(input_path)
    stats = ConversionStats(input_file=str(path))
    html = path.read_text(encoding="utf-8-sig")
    return flatten_html(html, stats=stats)


def flatten_html(html: str, stats: ConversionStats | None = None) -> FlatTable:
    rows = parse_html_tables(html)
    stats = stats or ConversionStats()
    stats.html_rows_read = len(rows)

    current_header: list[str] = []
    output_headers: list[str] = []
    output_rows: list[dict[str, object]] = []
    context: dict[str, str] = {}
    i = 0
    while i < len(rows):
        texts = _trim_trailing_empty(rows[i].texts)
        if _is_empty(texts) or _is_skip_row(texts):
            stats.skipped_rows += 1
            i += 1
            continue

        next_texts = _trim_trailing_empty(rows[i + 1].texts) if i + 1 < len(rows) else []
        group_from_pair = _context_from_label_value_rows(texts, next_texts)
        if group_from_pair:
            _merge_context(context, group_from_pair)
            stats.skipped_rows += 2
            i += 2
            continue

        if _looks_like_multi_header(texts, next_texts):
            current_header = _unique_headers(_combine_header_rows(texts, next_texts))
            _remember_header(stats, current_header)
            stats.skipped_rows += 2
            i += 2
            continue

        if _looks_like_header(texts):
            candidate = _unique_headers(texts)
            if candidate != current_header:
                current_header = candidate
                _remember_header(stats, current_header)
            stats.skipped_rows += 1
            i += 1
            continue

        mapped = _map_row(current_header, texts)
        context_update = _context_from_row(mapped, texts)
        if context_update and not _is_detail_row(mapped, current_header):
            _merge_context(context, context_update)
            stats.skipped_rows += 1
            i += 1
            continue

        if current_header and _is_detail_row(mapped, current_header):
            row = _apply_context(mapped, context, current_header)
            row = {key: _coerce_value(key, value) for key, value in row.items()}
            output_headers = _merge_headers(output_headers, list(row.keys()))
            output_rows.append(row)
            stats.exported_rows += 1
        else:
            stats.skipped_rows += 1
        i += 1

    return FlatTable(headers=output_headers, rows=output_rows, stats=stats)


def _trim_trailing_empty(values: list[str]) -> list[str]:
    result = [str(value).strip() for value in values]
    while result and result[-1] == "":
        result.pop()
    return result


def _is_empty(values: list[str]) -> bool:
    return not any(values)


def _is_skip_row(values: list[str]) -> bool:
    joined = " ".join(value for value in values if value)
    if not joined:
        return True
    if any(keyword.lower() in joined.lower() for keyword in SKIP_KEYWORDS):
        return True
    return bool(re.fullmatch(r"[\d.:/ -]+", joined)) and len([v for v in values if v]) <= 2


def _looks_like_header(values: list[str]) -> bool:
    meaningful = [value for value in values if value]
    if len(meaningful) < 2:
        return False
    hints = sum(1 for value in meaningful if value in HEADER_HINTS)
    numeric = sum(1 for value in meaningful if looks_numeric(value))
    return hints >= 2 and numeric == 0


def _looks_like_multi_header(values: list[str], next_values: list[str]) -> bool:
    if not values or not next_values:
        return False
    parent_hints = {"Счет", "Сальдо на начало периода", "Обороты за период", "Сальдо на конец периода"}
    child_hints = {"Код", "Наименование", "Дебет", "Кредит"}
    return (
        len([value for value in values if value in parent_hints]) >= 2
        and len([value for value in next_values if value in child_hints]) >= 3
    )


def _combine_header_rows(parents: list[str], children: list[str]) -> list[str]:
    width = max(len(parents), len(children))
    parents = parents + [""] * (width - len(parents))
    children = children + [""] * (width - len(children))
    headers: list[str] = []
    current_parent = ""
    for parent, child in zip(parents, children, strict=True):
        current_parent = parent or current_parent
        if current_parent and child:
            headers.append(f"{current_parent} {child}")
        else:
            headers.append(child or current_parent)
    return headers


def _unique_headers(headers: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    unique: list[str] = []
    for index, header in enumerate(headers, start=1):
        base = header.strip() or f"Column_{index}"
        count = seen.get(base, 0) + 1
        seen[base] = count
        unique.append(base if count == 1 else f"{base}_{count}")
    return unique


def _map_row(headers: list[str], values: list[str]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for header, value in zip(headers, values + [""] * max(0, len(headers) - len(values)), strict=False):
        mapped[header] = value.strip()
    return mapped


def _context_from_label_value_rows(values: list[str], next_values: list[str]) -> dict[str, str]:
    labels = [value for value in values if value]
    next_meaningful = [value for value in next_values if value]
    if len(labels) >= 1 and len(labels) == len(next_meaningful) and all(label in CONTEXT_FIELDS for label in labels):
        return dict(zip(labels, next_meaningful, strict=True))
    return {}


def _context_from_row(mapped: dict[str, str], values: list[str]) -> dict[str, str]:
    update = {field: mapped[field] for field in CONTEXT_FIELDS if mapped.get(field)}
    if update:
        return update
    if len(values) >= 2 and values[0] in CONTEXT_FIELDS and values[1]:
        return {values[0]: values[1]}
    if len(values) >= 4:
        pairs = {}
        for label, value in zip(values[0::2], values[1::2], strict=False):
            if label in CONTEXT_FIELDS and value:
                pairs[label] = value
        return pairs
    return {}


def _is_detail_row(mapped: dict[str, str], headers: list[str]) -> bool:
    if not headers or not any(mapped.values()):
        return False
    non_context_values = [value for key, value in mapped.items() if key not in CONTEXT_FIELDS and value]
    numeric_values = [value for key, value in mapped.items() if _is_numeric_column(key) and looks_numeric(value)]
    if numeric_values:
        return True
    return bool(non_context_values) and len([value for value in mapped.values() if value]) >= 2


def _apply_context(mapped: dict[str, str], context: dict[str, str], headers: list[str]) -> dict[str, str]:
    row: dict[str, str] = {}
    for field in CONTEXT_FIELDS:
        if field in headers:
            value = mapped.get(field, "")
            if value or context.get(field):
                row[field] = value or context.get(field, "")
        elif context.get(field):
            row[field] = context[field]
    for header in headers:
        if header in CONTEXT_FIELDS and header in row:
            continue
        row[header] = mapped.get(header, "")
    return row


def _coerce_value(header: str, value: str) -> object:
    if value == "":
        return ""
    if _is_numeric_column(header):
        return parse_localized_number(value)
    return value


def _is_numeric_column(header: str) -> bool:
    return any(word in header for word in NUMERIC_HEADER_WORDS)


def _merge_context(context: dict[str, str], update: dict[str, str]) -> None:
    for key, value in update.items():
        if value:
            context[key] = value


def _merge_headers(existing: list[str], new_headers: list[str]) -> list[str]:
    merged = list(existing)
    for header in new_headers:
        if header not in merged:
            merged.append(header)
    return merged


def _remember_header(stats: ConversionStats, header: list[str]) -> None:
    if header and header not in stats.detected_headers:
        stats.detected_headers.append(header)
