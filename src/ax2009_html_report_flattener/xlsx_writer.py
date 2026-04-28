"""XLSX writing utilities."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from .flattener import FlatTable


def write_xlsx(table: FlatTable, output_path: str | Path) -> None:
    path = Path(output_path)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Flat data"

    sheet.append(table.headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for row in table.rows:
        sheet.append([row.get(header, "") for header in table.headers])

    sheet.freeze_panes = "A2"
    if table.headers:
        sheet.auto_filter.ref = sheet.dimensions
    _auto_width(sheet)
    workbook.save(path)


def _auto_width(sheet) -> None:
    for column_cells in sheet.columns:
        letter = column_cells[0].column_letter
        max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
        sheet.column_dimensions[letter].width = min(max(max_length + 2, 10), 60)
