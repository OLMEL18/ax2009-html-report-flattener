# ax2009-html-report-flattener

A small Python desktop utility for Windows that converts Microsoft Dynamics AX 2009 / Dynamics-style HTML report exports into clean flat Excel workbooks.

The MVP reads `.htm` / `.html` files and writes one `.xlsx` file with a single worksheet named `Flat data`. It does not require Microsoft Excel to be installed.

## What It Handles

- AX/Dynamics HTML tables with repeated headers, page headers, report titles, spacer rows, service notes, subtotals, and grand totals.
- Inventory reports by warehouse or item group.
- Vendor transaction reports grouped by vendor, with supplier context carried into each detail row.
- General ledger trial balances with two-row headers such as `Сальдо на начало периода` + `Дебет`.
- Vendor trial balance-style reports where supplier and GL account context appears above detail rows.
- Ukrainian/Russian formatted numbers such as `55 440,0000`, `1 068 940,35`, and `-6 500,00`.

## Install

Use Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## CLI

```powershell
python -m ax2009_html_report_flattener.cli input.htm -o output.xlsx
```

The package also exposes a console script:

```powershell
ax2009-html-report-flattener input.htm -o output.xlsx
```

If `-o` is omitted, the output is saved next to the input file using the same base name plus `_flat.xlsx`.

## GUI

```powershell
python -m ax2009_html_report_flattener.cli --gui
```

The GUI lets you browse for a `.htm` / `.html` report, auto-fills the output `.xlsx` path, and shows exported/skipped row counts after conversion.

## Build Windows executable

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Build the one-file Windows GUI executable:

```powershell
.\build_exe.ps1
```

The generated executable is written to:

```powershell
dist\ax2009-html-report-flattener.exe
```

The generated EXE is a build artifact and should not be committed.

## Confidentiality Warning

Do not commit real business reports, company data, vendor data, item data, account balances, transaction data, or generated customer workbooks to this repository. Use only synthetic or anonymized fixtures for tests and examples.

## Current Limitations

- HTML input only; PDF is not supported.
- XLSX output only.
- No drag and drop.
- No profiles or configuration editor.
- No external services.
- Heuristic report detection is intentionally lightweight in v1 and may need tuning for unusual AX export layouts.

## Test

```powershell
python -m pytest
python -m ax2009_html_report_flattener.cli --help
```
