# NeoCompression

Adaptive binary compression tool that converts arbitrary files and folders into a compact, reversible ASCII representation using an adaptive chunking and pattern dictionary algorithm.

## ⚡ Quick Start (Windows Users)

### Method 1: One-Click Install (Recommended)

Open **Command Prompt** or **PowerShell** and run:

```bash
pip install https://github.com/Fizzolas/NeoCompression/archive/main.zip
```

Then launch the GUI:
```bash
neocompression
```

### Method 2: Manual Install from Downloaded ZIP

If you downloaded the ZIP file:

1. **Open Command Prompt** in the folder where you extracted the ZIP
2. Run this command (replace the path with where you extracted it):

```bash
pip install "C:\path\to\NeoCompression-main"
```

3. Launch with:
```bash
neocompression
```

### Method 3: Build Standalone Executable

```bash
git clone https://github.com/Fizzolas/NeoCompression.git
cd NeoCompression
pip install pyinstaller
pyinstaller --onefile --name NeoCompression --add-data "neocompression;neocompression" -w neocompression/gui.py
```

The executable will be in the `dist` folder.

## 📖 Usage

### GUI Mode (Easiest)

Simply run:
```bash
neocompression
```

Then drag and drop files/folders onto the window.

### Command Line Mode

**Compress:**
```bash
neocompression compress "game folder" archive.neo
```

**Extract:**
```bash
neocompression decompress archive.neo output_folder
```

**Short commands:**
```bash
neo c "folder" archive.neo   # compress
neo x archive.neo output     # extract
```

## 🔧 Requirements

- Python 3.10 or higher
- No external dependencies (pure Python)

## 📦 File Format

`.neo` files are self-contained containers that include:
- All compressed data
- Reconstruction keys
- File metadata
- Original directory structure

The format is text-based (ASCII) for maximum compatibility and corruption resistance.

## 📊 Performance

- **Highly repetitive data** (logs, game assets): 10:1 to 100:1 compression
- **Random data**: Minimal compression (may expand slightly)
- **Small files (<10MB)**: Use default settings
- **Large files/folders**: Use `--chunk-bits 32768` or higher

## 🛠️ Troubleshooting

**"Command not found" error:**
```bash
python -m neocompression
```

**Permission errors:**
Run Command Prompt as Administrator

**Slow compression:**
Increase chunk size: `--chunk-bits 65536`

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Support

For issues: https://github.com/Fizzolas/NeoCompression/issues
