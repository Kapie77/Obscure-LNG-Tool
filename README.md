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
- Font-aware character normalization
- Placeholder-safe rebuilding (Obscure 1)
- **Drag & Drop support** (Windows-friendly)
- UTF-8 workflow with game-safe encoding output
- No external dependencies

---

## 🚀 Usage

### 1️⃣ Drag & Drop (Recommended for most users)

Just **drag a file onto the executable or Python script**.

#### Drag a `.lng` file
- Automatically detects the game
- Extracts:
  - `.csv` (Obscure 1 & 2)
  - `.txt` (Obscure 2)
- For Obscure 1, also generates:
  - `.meta.json` (required for rebuilding)

#### Drag a `.csv` or `.txt` file
- Rebuilds a new `.lng`
- Output file name:
  - `*_new.lng`

---

### 2️⃣ Command Line Interface (CLI)

#### Obscure 1 — Extract:
For .csv:
```bash
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob1 --format csv
```
For .txt:
```bash
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob1 --format txt
```
For both:
```
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob1 --format both
```

#### Obscure 1 — Rebuild:
For .csv:
```bash
python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob1
```
For .txt:
```bash
python obscure_lng_tool.py build LANGUAGE.txt LANGUAGE.new.lng --game ob1
```

#### Obscure 2 — Extract:
For .csv:
```bash
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format csv
```
For .txt:
```bash
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format txt
```
For both:
```bash
python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format both
```

#### Obscure 2 — Rebuild:
For .csv:
```bash
python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob2
```
For .txt:
```bash
python obscure_lng_tool.py build LANGUAGE.txt LANGUAGE.new.lng --game ob2
```
Optional null-terminator:
```
python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob2 --add-null
```

## How It Works
### Obscure 1
- Scans the entire `.lng` file to locate the real header dynamically
- Extracts entries using the original binary structure:
  - Group
  - Entry ID
  - Encoding
  - Parameters
- Filters out:
  - Control tokens
  - Invalid font bytes
- Extracts menu labels only when applicable
- Generates a `.meta.json` containing:
  - Header offset
  - Entry count

#### Obscure 1 (Rebuild)
- Uses `.csv` + `.meta.json`
- Rebuilds the binary structure from scratch
- Enforces:
  - Correct entry order
  - Correct entry count
  - Valid placeholder usage (%s, %d, etc.)
- Automatically normalizes text to font-safe glyphs
- Encodes output using Windows-1252
- Prevents invalid characters and broken UI text

### Obscure 2
- Fully parses:
  - Language code
  - Groups
  - Entries
  - Metadata
- Fully reconstructs the binary structure
- UTF-8 compatible workflow
- Font & Character Compatibility
- Both games use custom font tables with limited glyph sets.
This tool:
- Automatically normalizes unsupported characters
- Replaces invalid glyphs with closest valid alternatives
- Prevents broken text in-game

## 🔤 Font & Character Compatibility
Both games use **custom font tables with limited glyph sets**.
This tool:
- Detects unsupported characters
- Normalizes accented letters safely
- Replaces invalid glyphs with closest supported equivalents
- Prevents invisible or corrupted text in-game

## Notes & Limitations
Always keep `.meta.json` for Obscure 1 rebuilds
Do not manually reorder CSV rows
Placeholder mismatches will abort rebuilding (by design)
Always test translations in-game
Backup original files before rebuilding