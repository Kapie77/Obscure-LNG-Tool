# Obscure LNG Tool

A cross-plataform CLI tool to **extract and rebuild `.lng` language files**
from **Obscure (2004)**, **Obscure II: The Aftermath (2007)** and **Final Exam (2013)**.

---

## 📦 Supported Games

| Game | Status |
|-----|------|------|
| Final Exam | Steam ✅ | Xbox ✅

# Como usar
## Extract
Converte .lng → arquivos editáveis:
- TXT (principal formato de tradução)
- CSV (formato alternativo estruturado)
- Both (gera os dois ao mesmo tempo)

Exemplo:

```python obscure_lng_tool.py extract it.lng --format txt```
```python obscure_lng_tool.py extract it.lng --format csv```
```python obscure_lng_tool.py extract it.lng --format both```

**Nota:**

translated ← campo vazio para tradutores

## Rebuild

Reconstrói o .lng a partir de:
- .txt
- .csv
Exemplo:

```python obscure_lng_tool.py rebuild it.txt```
```python obscure_lng_tool.py rebuild it.csv```
