"""Simple tkinter desktop GUI."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .cli import convert_file


class FlattenerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AX 2009 HTML Report Flattener")
        self.resizable(False, False)
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=14)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Input HTML").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(frame, textvariable=self.input_var, width=58).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Button(frame, text="Browse", command=self._browse_input).grid(row=0, column=2, padx=(8, 0), pady=4)

        ttk.Label(frame, text="Output XLSX").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(frame, textvariable=self.output_var, width=58).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(frame, text="Browse", command=self._browse_output).grid(row=1, column=2, padx=(8, 0), pady=4)

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=3, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="OK", command=self._run).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Cancel", command=self.destroy).grid(row=0, column=1)

    def _browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select HTML report",
            filetypes=[("HTML files", "*.htm *.html"), ("All files", "*.*")],
        )
        if path:
            self.input_var.set(path)
            input_path = Path(path)
            self.output_var.set(str(input_path.with_name(f"{input_path.stem}_flat.xlsx")))

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save XLSX as",
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx")],
        )
        if path:
            self.output_var.set(path)

    def _run(self) -> None:
        try:
            if not self.input_var.get().strip():
                raise ValueError("Select an input HTML file.")
            stats = convert_file(self.input_var.get().strip(), self.output_var.get().strip() or None)
        except Exception as exc:
            messagebox.showerror("Conversion failed", str(exc))
            return
        messagebox.showinfo(
            "Conversion complete",
            f"Output file: {stats.output_file}\nExported rows: {stats.exported_rows}\nSkipped rows: {stats.skipped_rows}",
        )


def main() -> None:
    app = FlattenerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
