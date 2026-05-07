import csv

MAX_CELL = 32000  # evita limite do Excel


# ==========================
#        EXPORT CSV
# ==========================
def export_csv(data, path):
    game = data.get("game", "finalexam")

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # =========================
        # FINAL EXAM
        # =========================
        if game in ["finalexam", "final_exam"]:

            writer.writerow([
                "index",
                "sid",
                "tag",
                "original",
                "translated"
            ])

            for entry in data.get("entries", []):
                index = entry.get("index", 0)
                sid = f"0x{entry.get('sid', 0):08X}"

                for tag, text in entry.get("subs", []):
                    text = text or ""
                    text = text.replace("\n", "\\n").replace("\r", "\\r")

                    if len(text) > MAX_CELL:
                        text = text[:MAX_CELL] + "..."

                    writer.writerow([
                        index,
                        sid,
                        f"0x{tag:04X}",
                        text,     # original
                        ""        # tradução
                    ])

        # =========================
        # OBSCURE 1
        # =========================
        elif game in ["ob1", "obscure1"]:

            writer.writerow([
                "index",
                "group",
                "id",
                "encoding",
                "original",
                "translated"
            ])

            for e in data.get("entries", []):
                text = e.get("text", "") or ""
                text = text.replace("\n", "\\n").replace("\r", "\\r")

                if len(text) > MAX_CELL:
                    text = text[:MAX_CELL] + "..."

                writer.writerow([
                    e.get("index", 0),
                    e.get("group", 0),
                    e.get("id", 0),
                    e.get("encoding", 0),
                    text,   # original
                    ""      # tradução
                ])

        else:
            raise ValueError(f"Unknown game type: {game}")


# ==========================
#        IMPORT CSV
# ==========================
def parse_csv(path):
    import csv

    entries = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        if "group" in headers:

            for row in reader:
                index = int(row.get("index", 0))

                entries[index] = {
                    "index": index,
                    "group": int(row.get("group", 0)),
                    "id": int(row.get("id", 0)),
                    "encoding": int(row.get("encoding", 0)),
                    "text": row.get("translated") or row.get("original") or row.get("text", "")
                }

            return {
                "game": "ob1",
                "entries": list(entries.values())
            }

        return {"game": "unknown", "entries": []}

        # ======================
        # FINAL EXAM CSV
        # ======================
        for row in reader:
            index = int(row.get("index", 0))
            sid = int(row.get("sid", "0"), 16)
            tag = int(row.get("tag", "0"), 16)

            original = row.get("original", "")
            translated = row.get("translated", "")

            text = translated if translated.strip() else original

            if index not in entries:
                entries[index] = {
                    "index": index,
                    "sid": sid,
                    "subs": []
                }

            entries[index]["subs"].append((tag, text))

        return {
            "game": "finalexam",
            "entries": list(entries.values())
        }