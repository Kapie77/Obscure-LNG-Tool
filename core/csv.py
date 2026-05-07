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
                "sid",
                "tag",
                "text"
            ])

            for entry in data.get("entries", []):
                sid = f"0x{entry.get('sid', 0):08X}"

                for tag, text in entry.get("subs", []):
                    text = (text or "").replace("\n", "\\n").replace("\r", "\\r")

                    writer.writerow([
                        sid,
                        f"0x{tag:04X}",
                        text
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
        
        # =========================
        # OBSCURE 2
        # =========================
        elif game in ["ob2", "obscure2"]:

            writer.writerow([
                "group_index",
                "group_id",
                "entry_index",
                "meta",
                "original",
                "translated"
            ])

            for e in data.get("entries", []):
                text = e.get("text", "") or ""
                text = text.replace("\n", "\\n").replace("\r", "\\r")

                if len(text) > MAX_CELL:
                    text = text[:MAX_CELL] + "..."

                writer.writerow([
                    e.get("group_index", 0),
                    e.get("group_id", 0),
                    e.get("entry_index", 0),
                    e.get("meta", 0),
                    text,
                    ""
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

        # =========================
        # OBSCURE 1 / OB2 / FINAL EXAM DETECTION
        # =========================

        if "group" in headers and "encoding" in headers:
            game = "ob1"
        elif "sid" in headers and "tag" in headers:
            game = "finalexam"
        else:
            game = "ob2"

        # =========================
        # OB1
        # =========================
        if game == "ob1":
            for row in reader:
                index = int(row.get("index", 0))

                entries[index] = {
                    "index": index,
                    "group": int(row.get("group", 0)),
                    "id": int(row.get("id", 0)),
                    "encoding": int(row.get("encoding", 0)),
                    "text": row.get("translated") or row.get("original") or ""
                }

            return {
                "game": "ob1",
                "entries": list(entries.values())
            }

        # =========================
        # FINAL EXAM
        # =========================
        if game == "finalexam":
            entries = {}

            for row in reader:
                sid = int(row["sid"], 16)
                tag = int(row["tag"], 16)
                text = row.get("text", "")

                if sid not in entries:
                    entries[sid] = {
                        "sid": sid,
                        "subs": []
                    }

                entries[sid]["subs"].append((tag, text))

            return {
                "game": "finalexam",
                "entries": list(entries.values())
            }

        # =========================
        # OB2 (SIMPLES - fallback)
        # =========================
        return {
            "game": "ob2",
            "entries": []
        }