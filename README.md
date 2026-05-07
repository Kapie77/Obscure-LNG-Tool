# Obscure LNG Tool

A cross-plataform CLI tool to extract and rebuild `.lng` files from **Obscure (2004)**, **Obscure II: The Aftermath (2007)** and **Final Exam (2013)**.

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
