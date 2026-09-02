"""Tkinter user interface for the edge detector project."""

from __future__ import annotations

import threading
import time
import tkinter as tk
from pathlib import Path
from queue import Empty, Queue
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from gradient_edge import gradient_edge
from simple_edge import simple_edge
from sobel_edge import sobel_edge


BACKGROUND = "#17181c"
SURFACE = "#212329"
SURFACE_ALT = "#292c33"
BORDER = "#363a44"
TEXT = "#f5f7fb"
MUTED = "#a7adba"
ACCENT = "#6c7cff"
ACCENT_ACTIVE = "#8290ff"
SUCCESS = "#57c785"
ERROR = "#ff6b6b"


ALGORITHMS = {
    "Simple": {
        "function": simple_edge,
        "threshold": 3,
        "threshold_max": 100,
        "uses_blur": True,
        "description": "Compares every pixel with its right and lower neighbours.",
    },
    "Gradient": {
        "function": gradient_edge,
        "threshold": 5,
        "threshold_max": 200,
        "uses_blur": True,
        "description": "Combines horizontal and vertical changes into a gradient magnitude.",
    },
    "Sobel": {
        "function": sobel_edge,
        "threshold": 40,
        "threshold_max": 500,
        "uses_blur": False,
        "description": "Uses Sobel kernels for stronger, directional edge detection.",
    },
}


class EdgeDetectorApp:
    """Main application window and UI state."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.image_path: Path | None = None
        self.source_image: Image.Image | None = None
        self.result_image: Image.Image | None = None
        self.result_algorithm: str | None = None
        self.source_photo: ImageTk.PhotoImage | None = None
        self.result_photo: ImageTk.PhotoImage | None = None
        self.is_processing = False
        self.result_queue: Queue = Queue()
        self._preview_refresh_job: str | None = None

        self.algorithm_var = tk.StringVar(value="Simple")
        self.threshold_var = tk.DoubleVar(value=3)
        self.threshold_text = tk.StringVar(value="3")
        self.blur_var = tk.DoubleVar(value=1.5)
        self.blur_text = tk.StringVar(value="1.5")
        self.source_details_var = tk.StringVar(value="Choose an image to begin")
        self.result_details_var = tk.StringVar(value="The detected edges will appear here")
        self.algorithm_description_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")

        self._configure_window()
        self._configure_styles()
        self._build_layout()
        self._on_algorithm_changed()

    def _configure_window(self) -> None:
        self.root.title("Edge Detector")
        self.root.geometry("1120x760")
        self.root.minsize(900, 650)
        self.root.configure(bg=BACKGROUND)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground=SURFACE_ALT,
            background=SURFACE_ALT,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=7,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", SURFACE_ALT), ("disabled", SURFACE)],
            foreground=[("readonly", TEXT), ("disabled", MUTED)],
            selectbackground=[("readonly", SURFACE_ALT)],
            selectforeground=[("readonly", TEXT)],
        )
        style.configure(
            "Accent.Horizontal.TProgressbar",
            troughcolor=SURFACE_ALT,
            background=ACCENT,
            bordercolor=SURFACE_ALT,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )

    def _build_layout(self) -> None:
        container = tk.Frame(self.root, bg=BACKGROUND)
        container.pack(fill="both", expand=True, padx=26, pady=(22, 16))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        self._build_header(container)
        self._build_controls(container)
        self._build_previews(container)
        self._build_status_bar(container)

    def _build_header(self, parent: tk.Widget) -> None:
        header = tk.Frame(parent, bg=BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(0, weight=1)

        title_group = tk.Frame(header, bg=BACKGROUND)
        title_group.grid(row=0, column=0, sticky="w")

        tk.Label(
            title_group,
            text="EDGE DETECTOR",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_group,
            text="Compare edge-detection algorithms on any image",
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        self.choose_button = self._button(
            header,
            "Choose image",
            self.choose_image,
            primary=True,
            width=15,
        )
        self.choose_button.grid(row=0, column=1, sticky="e")

    def _build_controls(self, parent: tk.Widget) -> None:
        controls = tk.Frame(
            parent,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=18,
            pady=14,
        )
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        controls.grid_columnconfigure(1, weight=1)
        controls.grid_columnconfigure(3, weight=1)

        tk.Label(
            controls,
            text="Algorithm",
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.algorithm_box = ttk.Combobox(
            controls,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS),
            state="readonly",
            width=15,
            style="Dark.TCombobox",
            font=("Segoe UI", 10),
        )
        self.algorithm_box.grid(row=0, column=1, sticky="w")
        self.algorithm_box.bind("<<ComboboxSelected>>", self._on_algorithm_changed)

        tk.Label(
            controls,
            text="Threshold",
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=2, sticky="w", padx=(24, 8))

        threshold_group = tk.Frame(controls, bg=SURFACE)
        threshold_group.grid(row=0, column=3, sticky="ew")
        threshold_group.grid_columnconfigure(0, weight=1)
        self.threshold_scale = tk.Scale(
            threshold_group,
            variable=self.threshold_var,
            from_=0,
            to=100,
            orient="horizontal",
            resolution=1,
            showvalue=False,
            command=self._update_threshold_text,
            bg=SURFACE,
            fg=TEXT,
            troughcolor=SURFACE_ALT,
            activebackground=ACCENT,
            highlightthickness=0,
            bd=0,
            sliderlength=18,
            length=180,
        )
        self.threshold_scale.grid(row=0, column=0, sticky="ew")
        tk.Label(
            threshold_group,
            textvariable=self.threshold_text,
            width=4,
            anchor="e",
            bg=SURFACE,
            fg=TEXT,
            font=("Consolas", 10, "bold"),
        ).grid(row=0, column=1, padx=(6, 0))

        tk.Label(
            controls,
            text="Blur",
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=4, sticky="w", padx=(24, 8))

        blur_group = tk.Frame(controls, bg=SURFACE)
        blur_group.grid(row=0, column=5, sticky="ew")
        blur_group.grid_columnconfigure(0, weight=1)
        self.blur_scale = tk.Scale(
            blur_group,
            variable=self.blur_var,
            from_=0,
            to=5,
            orient="horizontal",
            resolution=0.1,
            showvalue=False,
            command=self._update_blur_text,
            bg=SURFACE,
            fg=TEXT,
            troughcolor=SURFACE_ALT,
            activebackground=ACCENT,
            highlightthickness=0,
            bd=0,
            sliderlength=18,
            length=120,
        )
        self.blur_scale.grid(row=0, column=0, sticky="ew")
        tk.Label(
            blur_group,
            textvariable=self.blur_text,
            width=4,
            anchor="e",
            bg=SURFACE,
            fg=TEXT,
            font=("Consolas", 10, "bold"),
        ).grid(row=0, column=1, padx=(6, 0))

        tk.Label(
            controls,
            textvariable=self.algorithm_description_var,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        ).grid(row=1, column=0, columnspan=6, sticky="ew", pady=(10, 0))

    def _build_previews(self, parent: tk.Widget) -> None:
        preview_area = tk.Frame(parent, bg=BACKGROUND)
        preview_area.grid(row=2, column=0, sticky="nsew")
        preview_area.grid_columnconfigure(0, weight=1, uniform="preview")
        preview_area.grid_columnconfigure(1, weight=1, uniform="preview")
        preview_area.grid_rowconfigure(0, weight=1)

        source_card, self.source_preview = self._preview_card(
            preview_area,
            column=0,
            title="ORIGINAL",
            details_var=self.source_details_var,
            empty_text="Choose an image\nto see a preview",
        )
        source_card.grid_configure(padx=(0, 9))

        result_card, self.result_preview = self._preview_card(
            preview_area,
            column=1,
            title="DETECTED EDGES",
            details_var=self.result_details_var,
            empty_text="Run an algorithm\nto see the result",
        )
        result_card.grid_configure(padx=(9, 0))

    def _preview_card(
        self,
        parent: tk.Widget,
        column: int,
        title: str,
        details_var: tk.StringVar,
        empty_text: str,
    ) -> tuple[tk.Frame, tk.Label]:
        card = tk.Frame(
            parent,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        card.grid(row=0, column=column, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        top = tk.Frame(card, bg=SURFACE, padx=16, pady=12)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        tk.Label(
            top,
            text=title,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            top,
            textvariable=details_var,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).grid(row=0, column=1, sticky="e")

        preview = tk.Label(
            card,
            text=empty_text,
            bg=SURFACE_ALT,
            fg=MUTED,
            font=("Segoe UI", 13),
            justify="center",
            compound="center",
        )
        preview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        preview.bind("<Configure>", self._schedule_preview_refresh)
        return card, preview

    def _build_status_bar(self, parent: tk.Widget) -> None:
        footer = tk.Frame(parent, bg=BACKGROUND)
        footer.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        footer.grid_columnconfigure(1, weight=1)

        self.run_button = self._button(
            footer,
            "Run detection",
            self.run_detection,
            primary=True,
            width=16,
            state="disabled",
        )
        self.run_button.grid(row=0, column=0, sticky="w")

        status_group = tk.Frame(footer, bg=BACKGROUND)
        status_group.grid(row=0, column=1, sticky="ew", padx=(16, 10))
        status_group.grid_columnconfigure(1, weight=1)

        self.progress = ttk.Progressbar(
            status_group,
            mode="indeterminate",
            length=120,
            style="Accent.Horizontal.TProgressbar",
        )
        self.progress.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.progress.grid_remove()

        self.status_label = tk.Label(
            status_group,
            textvariable=self.status_var,
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.status_label.grid(row=0, column=1, sticky="w")

        self.save_button = self._button(
            footer,
            "Save result",
            self.save_result,
            width=14,
            state="disabled",
        )
        self.save_button.grid(row=0, column=2, sticky="e", padx=(10, 0))

        self.clear_button = self._button(
            footer,
            "Clear",
            self.clear,
            width=10,
        )
        self.clear_button.grid(row=0, column=3, sticky="e", padx=(10, 0))

    def _button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        primary: bool = False,
        **kwargs,
    ) -> tk.Button:
        bg = ACCENT if primary else SURFACE_ALT
        active_bg = ACCENT_ACTIVE if primary else BORDER
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=TEXT,
            activebackground=active_bg,
            activeforeground=TEXT,
            disabledforeground="#737986",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            cursor="hand2",
            **kwargs,
        )

    def choose_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp *.ico"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            with Image.open(file_path) as image:
                source_image = image.copy()
        except (OSError, ValueError) as exc:
            messagebox.showerror("Cannot open image", f"The selected file is not a valid image.\n\n{exc}")
            return

        self.image_path = Path(file_path)
        self.source_image = source_image
        self.result_image = None
        self.result_algorithm = None
        self.source_details_var.set(
            f"{source_image.width} × {source_image.height}  •  {source_image.mode}"
        )
        self.result_details_var.set("The detected edges will appear here")
        self._show_image(source_image, self.source_preview, "source")
        self._clear_preview(self.result_preview, "Run an algorithm\nto see the result")
        self.run_button.configure(state="normal")
        self.save_button.configure(state="disabled")
        self.status_var.set(f"Loaded {self.image_path.name}")
        self.status_label.configure(fg=MUTED)

    def run_detection(self) -> None:
        if self.image_path is None or self.is_processing:
            if self.image_path is None:
                messagebox.showinfo("Choose an image", "Choose an image before running edge detection.")
            return

        algorithm = self.algorithm_var.get()
        threshold = int(round(self.threshold_var.get()))
        blur_radius = round(self.blur_var.get(), 1)
        path = str(self.image_path)

        self._set_busy(True)
        self.status_var.set(f"Running {algorithm} edge detection…")
        self.status_label.configure(fg=MUTED)

        worker = threading.Thread(
            target=self._process_image,
            args=(path, algorithm, threshold, blur_radius),
            daemon=True,
        )
        worker.start()
        self.root.after(50, self._poll_result_queue)

    def _process_image(
        self,
        path: str,
        algorithm: str,
        threshold: int,
        blur_radius: float,
    ) -> None:
        started = time.perf_counter()
        try:
            config = ALGORITHMS[algorithm]
            detector = config["function"]
            if config["uses_blur"]:
                result = detector(path, threshold=threshold, blur_radius=blur_radius)
            else:
                result = detector(path, threshold=threshold)
            elapsed = time.perf_counter() - started
            self.result_queue.put(("success", result, algorithm, elapsed))
        except Exception as exc:  # UI boundary: show detector and image errors cleanly.
            self.result_queue.put(("error", exc))

    def _poll_result_queue(self) -> None:
        try:
            outcome = self.result_queue.get_nowait()
        except Empty:
            if self.is_processing:
                self.root.after(50, self._poll_result_queue)
            return

        if outcome[0] == "success":
            _, result, algorithm, elapsed = outcome
            self._finish_processing(result, algorithm, elapsed)
        else:
            _, exc = outcome
            self._processing_failed(exc)

    def _finish_processing(
        self,
        result: Image.Image,
        algorithm: str,
        elapsed: float,
    ) -> None:
        self.result_image = result.copy()
        self.result_algorithm = algorithm
        self._show_image(self.result_image, self.result_preview, "result")
        self.result_details_var.set(
            f"{result.width} × {result.height}  •  {algorithm}  •  {elapsed:.2f}s"
        )
        self.status_var.set(f"{algorithm} detection completed in {elapsed:.2f} seconds")
        self.status_label.configure(fg=SUCCESS)
        self._set_busy(False)
        self.save_button.configure(state="normal")

    def _processing_failed(self, exc: Exception) -> None:
        self._set_busy(False)
        self.status_var.set("Edge detection failed")
        self.status_label.configure(fg=ERROR)
        messagebox.showerror("Edge detection failed", str(exc))

    def save_result(self) -> None:
        if self.result_image is None:
            return

        source_stem = self.image_path.stem if self.image_path else "image"
        algorithm = (self.result_algorithm or self.algorithm_var.get()).lower()
        destination = filedialog.asksaveasfilename(
            title="Save detected edges",
            defaultextension=".png",
            initialfile=f"{source_stem}_{algorithm}_edges.png",
            filetypes=[
                ("PNG image", "*.png"),
                ("JPEG image", "*.jpg *.jpeg"),
                ("Bitmap image", "*.bmp"),
                ("TIFF image", "*.tif *.tiff"),
            ],
        )
        if not destination:
            return

        try:
            self.result_image.save(destination)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Could not save image", str(exc))
            return

        self.status_var.set(f"Saved {Path(destination).name}")
        self.status_label.configure(fg=SUCCESS)

    def clear(self) -> None:
        if self.is_processing:
            return
        self.image_path = None
        self.source_image = None
        self.result_image = None
        self.result_algorithm = None
        self.source_photo = None
        self.result_photo = None
        self.source_details_var.set("Choose an image to begin")
        self.result_details_var.set("The detected edges will appear here")
        self._clear_preview(self.source_preview, "Choose an image\nto see a preview")
        self._clear_preview(self.result_preview, "Run an algorithm\nto see the result")
        self.run_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.status_var.set("Ready")
        self.status_label.configure(fg=MUTED)

    def _on_algorithm_changed(self, _event=None) -> None:
        config = ALGORITHMS[self.algorithm_var.get()]
        default_threshold = config["threshold"]
        self.threshold_scale.configure(to=config["threshold_max"])
        self.threshold_var.set(default_threshold)
        self.threshold_text.set(str(default_threshold))
        self.algorithm_description_var.set(config["description"])

        blur_state = "normal" if config["uses_blur"] else "disabled"
        self.blur_scale.configure(state=blur_state)
        self.blur_text.set(f"{self.blur_var.get():.1f}" if config["uses_blur"] else "—")

    def _update_threshold_text(self, value: str) -> None:
        self.threshold_text.set(str(int(round(float(value)))))

    def _update_blur_text(self, value: str) -> None:
        if ALGORITHMS[self.algorithm_var.get()]["uses_blur"]:
            self.blur_text.set(f"{float(value):.1f}")

    def _set_busy(self, busy: bool) -> None:
        self.is_processing = busy
        if busy:
            self.run_button.configure(state="disabled")
            self.choose_button.configure(state="disabled")
            self.save_button.configure(state="disabled")
            self.clear_button.configure(state="disabled")
            self.algorithm_box.configure(state="disabled")
            self.progress.grid()
            self.progress.start(12)
        else:
            self.progress.stop()
            self.progress.grid_remove()
            self.run_button.configure(state="normal" if self.image_path else "disabled")
            self.choose_button.configure(state="normal")
            self.clear_button.configure(state="normal")
            self.algorithm_box.configure(state="readonly")

    def _show_image(self, image: Image.Image, label: tk.Label, target: str) -> None:
        available_width = max(label.winfo_width() - 24, 200)
        available_height = max(label.winfo_height() - 24, 200)
        preview = image.copy()
        preview.thumbnail((available_width, available_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(preview)
        label.configure(image=photo, text="")
        if target == "source":
            self.source_photo = photo
        else:
            self.result_photo = photo

    def _clear_preview(self, label: tk.Label, text: str) -> None:
        label.configure(image="", text=text)

    def _schedule_preview_refresh(self, _event=None) -> None:
        if self._preview_refresh_job is not None:
            self.root.after_cancel(self._preview_refresh_job)
        self._preview_refresh_job = self.root.after(120, self._refresh_previews)

    def _refresh_previews(self) -> None:
        self._preview_refresh_job = None
        if self.source_image is not None:
            self._show_image(self.source_image, self.source_preview, "source")
        if self.result_image is not None:
            self._show_image(self.result_image, self.result_preview, "result")


def run() -> None:
    root = tk.Tk()
    EdgeDetectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
