"""Small formatting helpers for conversion diagnostics."""

from __future__ import annotations

from .flattener import ConversionStats


def format_stats(stats: ConversionStats) -> str:
    lines = [
        f"Input file: {stats.input_file}",
        f"Output file: {stats.output_file}",
        f"HTML rows read: {stats.html_rows_read}",
        f"Exported rows: {stats.exported_rows}",
        f"Skipped rows: {stats.skipped_rows}",
        "Detected headers:",
    ]
    if stats.detected_headers:
        lines.extend(f"  - {', '.join(header)}" for header in stats.detected_headers)
    else:
        lines.append("  - none")
    if stats.warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in stats.warnings)
    return "\n".join(lines)
