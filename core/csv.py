import csv

# ==========================
#          .CSV
# ==========================

# EXPORT
def export_csv(data, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # novo header
        writer.writerow(["index", "sid", "tag", "original", "translated"])

        for entry in data["entries"]:
            index = entry["index"]
            sid = f"0x{entry['sid']:08X}"

            for tag, text in entry["subs"]:
                writer.writerow([
                    index,
                    sid,
                    f"0x{tag:04X}",
                    text,
                    ""  # campo vazio pra tradução
                ])

# IMPORT
def parse_csv(path):
    import csv
    entries = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            index = int(row["index"])
            sid = int(row["sid"], 16)
            tag = int(row["tag"], 16)

            original = row.get("original", "")
            translated = row.get("translated", "")

            # usa traduzido se tiver, senão original
            text = translated if translated.strip() else original

            if index not in entries:
                entries[index] = {
                    "sid": sid,
                    "subs": []
                }

            entries[index]["subs"].append((tag, text))

    # ordenar
    result = []
    for i in sorted(entries.keys()):
        result.append({
            "index": i,
            "sid": entries[i]["sid"],
            "subs": entries[i]["subs"]
        })

    return result