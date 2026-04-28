"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .flattener import convert_html_to_flat_table
from .logging_utils import format_stats
from .xlsx_writer import write_xlsx


def convert_file(input_path: str | Path, output_path: str | Path | None = None):
    input_file = Path(input_path)
    if input_file.suffix.lower() not in {".htm", ".html"}:
        raise ValueError("Input file must be .htm or .html")
    output_file = Path(output_path) if output_path else input_file.with_name(f"{input_file.stem}_flat.xlsx")
    table = convert_html_to_flat_table(input_file)
    table.stats.output_file = str(output_file)
    write_xlsx(table, output_file)
    return table.stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Flatten Dynamics AX 2009-style HTML reports to XLSX.")
    parser.add_argument("input", nargs="?", help="Input .htm/.html report export")
    parser.add_argument("-o", "--output", help="Output .xlsx path")
    parser.add_argument("--gui", action="store_true", help="Open the tkinter GUI")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.gui:
        from .gui import main as gui_main

        gui_main()
        return 0
    if not args.input:
        parser.error("input is required unless --gui is used")
    stats = convert_file(args.input, args.output)
    print(format_stats(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
