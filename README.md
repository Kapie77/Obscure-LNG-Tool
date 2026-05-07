# Obscure LNG Tool

A cross-plataform CLI tool to extract (converting them to editable formats such as .txt and .csv) and rebuild `.lng` files from **Obscure (2004)**, **Obscure II: The Aftermath (2007)** and **Final Exam (2013)**.

---

## 📦 Supported Games

| Game | Status |  |  |
|-----|------|------|------|
| Obscure 1 | Steam ✅ | Xbox ✅ | PS2 ✅
| Obscure 2 | Steam ✅ | PS2 ✅ | PSP ✅
| Final Exam | Steam ✅ | Xbox ✅ | PS3 ✅

---
# Usage
## Windows
### Extract:
Just drag a file onto the executable obscure_lng_tool.exe and select the format you want (.txt, .csv or both) by entering the corresponding number or the format name.


**Note:** The “translated” field in the .csv file is where you should enter the translations.


#### Rebuild
Drag the .txt or .csv file onto obscure_lng_tool.exe, and a .new.lng file will be generated automatically.

---
## Linux
### Command Line Interface (CLI)

#### Extract:
For .csv:
```bash
obscure_lng_tool.exe extract FILENAME.lng --format csv
```
For .txt:
```bash
obscure_lng_tool.exe extract FILENAME.lng --format txt
```
For both:
```
obscure_lng_tool.exe extract FILENAME.lng --format both
```

#### rebuild:
For .csv:
```bash
obscure_lng_tool.exe rebuild FILENAME.csv
```
```bash
obscure_lng_tool.exe rebuild FILENAME.txt
```

# How .lng files work
Each game uses a different structure, but they all follow the same concept:
- A header (metadata)
- A table of entries
- A block of strings (final text)

## Obscure 1
**Structure:**
- Header:
  - languageCode
  - entryCount
**Each entry contains:**
  - group (category)
  - id (text identifier)
  - encoding (text type)
  - param (optional)
  - raw text

**Features:**
- Encoding options:
  - CP1252 (plain text)
  - UTF-16LE (special cases)
- Text may contain replaced button tokens such as:
  - ÷ → [L1]
  - Æ → [R1]

## Obscure 2
**Structure:**
- Based on text groups
- Each entry contains:
  - group_index
  - group_id
  - entry_index
  - meta
  - text
**Features:**
- More modular organization than Obscure 1
- Used primarily in menus and structured UI
- Texts are more “grouped by system”

## Final Exam
More complex structure:
**Header:**
- v1 (file version)
- magic (game identifier)
- glyph table (UTF-32 characters)
**Entries:**
Each entry contains:
- sid (string ID)
- sub-entries (multiple lines of text per entry)
- Sub-entries:
**Each text has:**
- tag (caption type / context)
- offset (position in the string block)

**How the strings work:**
The game does NOT save strings directly in each entry.
It uses:
```offsets within a continuous block of text```
In other words:
- All strings are stored in a single “string pool”
- Each entry points to parts of that block using offsets

**How the rebuild works**
1. Rebuilds the string block from scratch
2. Each text is written sequentially
3. Each position becomes an offset
4. The offsets are combined with the original tags
5. The final file is reconstructed byte by byte

# How the tool manages to extract everything

The tool performs direct reverse engineering of the format:
1. Binary reading
- Uses struct to interpret little-endian/big-endian bytes
2. Parsing the input table
- Reads IDs, groups, and counters
3. String decoding
- CP1252 or UTF-16LE depending on the field
- Removes null terminators
4. Logical reconstruction
- Converts everything to a Python structure:
```bash
{
  "game": "...",
  "entries": [...]
}
```
