import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from threading import Thread

from .core import compress_path, decompress_file


class NeoCompressionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoCompression - Digital DVD")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")

        # Make window accept drag & drop files
        try:
            self.root.drop_target_register("DND_Files")
            self.root.dnd_bind("<<Drop>>", self.on_drop)
        except Exception:
            pass  # DnD not available on all platforms

        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="NeoCompression",
            font=("Segoe UI", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
        )
        title.pack(pady=20)

        # Subtitle
        subtitle = tk.Label(
            self.root,
            text="Convert any file/folder into a compact, reversible container",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            fg="#7f8c8d",
        )
        subtitle.pack(pady=5)

        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=20)

        # Compress button
        compress_btn = tk.Button(
            btn_frame,
            text="📦 Compress File/Folder",
            command=self.compress_dialog,
            font=("Segoe UI", 12),
            bg="#3498db",
            fg="white",
            width=20,
            height=2,
            cursor="hand2",
        )
        compress_btn.pack(side=tk.LEFT, padx=10)

        # Decompress button
        decompress_btn = tk.Button(
            btn_frame,
            text="📂 Extract .neo File",
            command=self.decompress_dialog,
            font=("Segoe UI", 12),
            bg="#2ecc71",
            fg="white",
            width=20,
            height=2,
            cursor="hand2",
        )
        decompress_btn.pack(side=tk.LEFT, padx=10)

        # Drop zone
        drop_zone = tk.Label(
            self.root,
            text="\n\nDrag & Drop files/folders here\n\n",
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#95a5a6",
            relief="solid",
            borderwidth=2,
        )
        drop_zone.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)

        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(
            self.root, mode="indeterminate", length=400
        )

        # Status label
        self.status = tk.Label(
            self.root, text="Ready", bg="#f0f0f0", fg="#2c3e50", font=("Segoe UI", 9)
        )
        self.status.pack(pady=5)

        # Version info
        version = tk.Label(
            self.root,
            text="v1.0.0",
            font=("Segoe UI", 8),
            bg="#f0f0f0",
            fg="#bdc3c7",
        )
        version.pack(side=tk.BOTTOM, pady=5)

    def on_drop(self, event):
        """Handle drag and drop files"""
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            path = Path(file_path)
            if path.suffix.lower() == ".neo":
                self.decompress_file(path)
            else:
                self.compress_file(path)
            break  # Only process first dropped item

    def compress_dialog(self):
        """Open file dialog for compression"""
        path = filedialog.askdirectory(title="Select Folder to Compress")
        if not path:
            path = filedialog.askopenfilename(title="Select File to Compress")
        if path:
            self.compress_file(Path(path))

    def decompress_dialog(self):
        """Open file dialog for decompression"""
        path = filedialog.askopenfilename(
            title="Select .neo file to extract",
            filetypes=[("NeoCompression files", "*.neo"), ("All files", "*.*")],
        )
        if path:
            self.decompress_file(Path(path))

    def compress_file(self, source_path: Path):
        """Compress a file or folder"""
        if not source_path.exists():
            messagebox.showerror("Error", f"Path not found: {source_path}")
            return

        # Ask for output location
        if source_path.is_file():
            default_name = source_path.stem + ".neo"
        else:
            default_name = source_path.name + ".neo"

        output_path = filedialog.asksaveasfilename(
            title="Save Compressed File",
            initialfile=default_name,
            defaultextension=".neo",
            filetypes=[("NeoCompression files", "*.neo")],
        )

        if not output_path:
            return

        self.run_compression(source_path, Path(output_path))

    def decompress_file(self, neo_path: Path):
        """Decompress a .neo file"""
        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Extract Destination")
        if not output_dir:
            return

        self.run_decompression(neo_path, Path(output_dir))

    def run_compression(self, source: Path, output: Path):
        """Run compression in background thread"""
        self.status.config(text=f"Compressing {source.name}...")
        self.progress.pack(pady=10)
        self.progress.start()

        def task():
            try:
                compress_path(source, output)
                self.root.after(0, lambda: self.on_complete(f"Compressed to {output.name}"))
            except Exception as e:
                self.root.after(0, lambda: self.on_error(str(e)))

        Thread(target=task, daemon=True).start()

    def run_decompression(self, container: Path, output_dir: Path):
        """Run decompression in background thread"""
        self.status.config(text=f"Extracting {container.name}...")
        self.progress.pack(pady=10)
        self.progress.start()

        def task():
            try:
                decompress_file(container, output_dir)
                self.root.after(0, lambda: self.on_complete(f"Extracted to {output_dir}"))
            except Exception as e:
                self.root.after(0, lambda: self.on_error(str(e)))

        Thread(target=task, daemon=True).start()

    def on_complete(self, message: str):
        """Called when operation completes successfully"""
        self.progress.stop()
        self.progress.pack_forget()
        self.status.config(text=message, fg="#27ae60")
        messagebox.showinfo("Success", message)
        self.root.after(3000, lambda: self.status.config(text="Ready", fg="#2c3e50"))

    def on_error(self, error: str):
        """Called when operation fails"""
        self.progress.stop()
        self.progress.pack_forget()
        self.status.config(text="Error occurred", fg="#e74c3c")
        messagebox.showerror("Error", f"Operation failed:\n{error}")
        self.root.after(3000, lambda: self.status.config(text="Ready", fg="#2c3e50"))


def run_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    app = NeoCompressionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
