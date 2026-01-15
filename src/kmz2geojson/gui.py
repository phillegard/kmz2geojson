"""Tkinter GUI for KMZ to GeoJSON converter."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from typing import Optional

from kmz2geojson.converter import KMZConverter
from kmz2geojson.exceptions import ConversionError


class KMZ2GeoJSONApp:
    """Main GUI application for KMZ to GeoJSON conversion."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("KMZ to GeoJSON Converter")
        self.root.geometry("550x280")
        self.root.minsize(450, 250)

        # State
        self.input_path: Optional[Path] = None
        self.output_path: Optional[Path] = None
        self.conversion_thread: Optional[threading.Thread] = None
        self.is_converting = False
        self.result = None
        self.conversion_error = None

        # Tkinter variables
        self.compact_var = tk.BooleanVar(value=False)
        self.verbose_var = tk.BooleanVar(value=False)

        self._create_widgets()
        self._configure_grid()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Input file row
        ttk.Label(main_frame, text="Input File:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.input_entry = ttk.Entry(main_frame, state="readonly", width=50)
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.input_btn = ttk.Button(
            main_frame, text="Browse...", command=self._browse_input
        )
        self.input_btn.grid(row=0, column=2, pady=5)

        # Output file row
        ttk.Label(main_frame, text="Output File:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.output_entry = ttk.Entry(main_frame, state="readonly", width=50)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.output_btn = ttk.Button(
            main_frame, text="Browse...", command=self._browse_output
        )
        self.output_btn.grid(row=1, column=2, pady=5)

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

        self.compact_check = ttk.Checkbutton(
            options_frame, text="Compact JSON output", variable=self.compact_var
        )
        self.compact_check.grid(row=0, column=0, sticky="w", padx=10)

        self.verbose_check = ttk.Checkbutton(
            options_frame, text="Verbose mode", variable=self.verbose_var
        )
        self.verbose_check.grid(row=0, column=1, sticky="w", padx=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            main_frame, mode="indeterminate", length=300
        )
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Ready")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)

        # Convert button
        self.convert_btn = ttk.Button(
            main_frame, text="Convert", command=self._start_conversion
        )
        self.convert_btn.grid(row=5, column=0, columnspan=3, pady=15)

        # Configure column weights
        main_frame.columnconfigure(1, weight=1)

    def _configure_grid(self):
        """Configure grid weights for responsive resizing."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _browse_input(self):
        """Open file dialog for input file selection."""
        filepath = filedialog.askopenfilename(
            title="Select KMZ or KML file",
            filetypes=[
                ("KMZ/KML files", "*.kmz *.kml"),
                ("KMZ files", "*.kmz"),
                ("KML files", "*.kml"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            self.input_path = Path(filepath)
            self.input_entry.config(state="normal")
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filepath)
            self.input_entry.config(state="readonly")

            # Auto-suggest output filename
            if not self.output_path:
                suggested = self.input_path.with_suffix(".geojson")
                self._set_output_path(suggested)

    def _browse_output(self):
        """Open file dialog for output file selection."""
        initial_name = "output.geojson"
        initial_dir = None
        if self.input_path:
            initial_name = self.input_path.stem + ".geojson"
            initial_dir = str(self.input_path.parent)

        filepath = filedialog.asksaveasfilename(
            title="Save GeoJSON file",
            defaultextension=".geojson",
            initialfile=initial_name,
            initialdir=initial_dir,
            filetypes=[
                ("GeoJSON files", "*.geojson"),
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            self._set_output_path(Path(filepath))

    def _set_output_path(self, path: Path):
        """Set the output path and update display."""
        self.output_path = path
        self.output_entry.config(state="normal")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, str(path))
        self.output_entry.config(state="readonly")

    def _set_ui_converting(self, converting: bool):
        """Enable or disable UI elements during conversion."""
        state = "disabled" if converting else "normal"
        self.input_btn.config(state=state)
        self.output_btn.config(state=state)
        self.convert_btn.config(state=state)
        self.compact_check.config(state=state)
        self.verbose_check.config(state=state)

    def _start_conversion(self):
        """Start conversion in background thread."""
        if self.is_converting:
            return

        if not self.input_path:
            messagebox.showerror("Error", "Please select an input file")
            return

        if not self.output_path:
            messagebox.showerror("Error", "Please select an output location")
            return

        self.is_converting = True
        self._set_ui_converting(True)
        self.status_label.config(text="Status: Converting...")
        self.progress_bar.start(10)

        # Reset result
        self.result = None
        self.conversion_error = None

        # Create and start worker thread
        self.conversion_thread = threading.Thread(
            target=self._conversion_worker, daemon=True
        )
        self.conversion_thread.start()

        # Start polling for completion
        self._poll_conversion()

    def _conversion_worker(self):
        """Worker thread that performs the actual conversion."""
        try:
            converter = KMZConverter()

            if self.verbose_var.get():
                print(f"Converting: {self.input_path}")
                print(f"Output: {self.output_path}")
                print(f"Compact: {self.compact_var.get()}")

            self.result = converter.convert(
                input_path=self.input_path,
                output_path=self.output_path,
                pretty=not self.compact_var.get(),
                validate=True,
            )

            if self.verbose_var.get():
                feature_count = len(self.result.get("features", []))
                print(f"Converted {feature_count} features")

        except ConversionError as e:
            self.conversion_error = e
        except Exception as e:
            self.conversion_error = Exception(f"Unexpected error: {e}")

    def _poll_conversion(self):
        """Poll for conversion thread completion using after()."""
        if self.conversion_thread and self.conversion_thread.is_alive():
            # Check again in 100ms
            self.root.after(100, self._poll_conversion)
        else:
            # Conversion finished
            self._on_conversion_complete()

    def _on_conversion_complete(self):
        """Handle conversion completion on main thread."""
        self.is_converting = False
        self._set_ui_converting(False)
        self.progress_bar.stop()

        if self.conversion_error:
            messagebox.showerror("Conversion Error", str(self.conversion_error))
            self.status_label.config(text="Status: Error")
        else:
            feature_count = len(self.result.get("features", []))
            messagebox.showinfo(
                "Success", f"Converted {feature_count} feature(s) successfully!"
            )
            self.status_label.config(text=f"Status: Converted {feature_count} features")


def main():
    """Main entry point for GUI application."""
    # Enable DPI awareness on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()

    # Set window icon (removes default Tk icon on Windows)
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass

    KMZ2GeoJSONApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
