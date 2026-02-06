# Obscure LNG Tool

A unified command-line and drag & drop tool to **extract and rebuild `.lng` language files**
from **Obscure (2004)** and **Obscure II: The Aftermath (2007)**.

---

## 📦 Supported Games

| Game | Status |
|-----|------|
| Obscure (2004) | Steam ✅ |
| Obscure II: The Aftermath (2007) | Steam ✅ |

---

## ✨ Features

- Supports **Obscure 1** and **Obscure 2**
- Extract `.lng` files to:
  - CSV
  - TXT
- Rebuild `.lng` files from edited CSV
- Automatic game detection (OB1 / OB2)
- Safe rebuilding (original file size preserved for Obscure 1)
- Font-aware character normalization (game-compatible glyph mapping)
- **Drag & Drop support** (Windows-friendly)
- Cross-language friendly (UTF-8 / Windows-1252)

---

## 🚀 Usage

### 1️⃣ Drag & Drop (Recommended for most users)

Just **drag a file onto the executable or Python script**.

#### Drag a `.lng` file
- Automatically detects the game
- Extracts text to:
  - `.csv` (Obscure 1 & 2)
  - `.txt` (Obscure 2)

#### Drag a `.csv` or `.txt` file
- Rebuilds a new `.lng`
- Output file name:
  - `*_new.lng`

⚠️ For **Obscure 1**, the original `.lng` file **must be present in the same folder**.

---

### 2️⃣ Command Line Interface (CLI)

#### Extract – Obscure 1
```bash
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob1 --format csv
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob1 --format both
```

#### Rebuild – Obscure 1
```bash
python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob1 --original LANGUAGE.lng
```

#### Extract – Obscure 2
```bash
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format csv
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format both
```

#### Rebuild – Obscure 2
```bash
python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob2
Optional null-terminator:
python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob2 --add-null
```

## How It Works
Obscure 1
Scans the .lng file for null-terminated strings
Preserves:
Original offsets
Maximum string length
File size
Uses Windows-1252 compatible encoding
Prevents buffer overflows automatically

### Obscure 2
Parses:
Language code
Groups
Entries
Metadata
Fully reconstructs the binary structure
UTF-8 compatible workflow

Font & Character Compatibility
Both games use custom font tables with limited glyph sets.
This tool:
Automatically normalizes unsupported characters
Replaces invalid glyphs with closest valid alternatives
Prevents broken text in-game

## Notes & Limitations
Obscure 1 requires the original .lng file for rebuilding
Do not exceed original string lengths in Obscure 1
Always test translations in-game
Backup original files before rebuilding
