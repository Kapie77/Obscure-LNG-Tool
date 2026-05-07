# ==========================
#          .TXT
# ==========================

# =====================
#        PARSE
# =====================
def parse_txt(content: str):
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    header = {}
    entries = []

    parts = content.split("### ENTRY")

    header_part = parts[0] if parts else ""

    for line in header_part.split("\n"):
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            header[k.strip().lower()] = v.strip()

    for sec in parts[1:]:
        sec = sec.strip()
        if not sec:
            continue

        close = sec.find("###")
        if close == -1:
            continue

        meta = sec[:close]
        body = sec[close + 3:].strip()

        body = body.replace("\\r", "\r").replace("\\n", "\n")

        entry = {
            "index": 0,
            "group": 0,
            "id": 0,
            "encoding": 0,
            "param": 0,
            "text": body
        }

        for line in meta.split("\n"):
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip().lower()
                v = v.strip()

                if k == "index":
                    entry["index"] = int(v)
                elif k == "group":
                    entry["group"] = int(v)
                elif k == "id":
                    entry["id"] = int(v)
                elif k == "encoding":
                    entry["encoding"] = int(v)
                elif k == "param":
                    entry["param"] = int(v)

        entries.append(entry)

    game = header.get("game", "ob1").strip().lower()

    return {
        "game": game,
        "header": header,
        "entries": entries
    }


# =====================
#       EXPORT
# =====================
def export_txt(data, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:

        game = data.get("game", "").lower()

        # ======================
        # HEADER
        # ======================
        f.write("### LANGUAGE\n")
        f.write(f"game = {game}\n")

        if game == "finalexam":
            f.write(f"v1 = {data.get('v1', 0)}\n")
            f.write(f"magic = 0x{data.get('magic', 0):08X}\n")
            f.write(
                "glyphs = " +
                ",".join(f"0x{x:X}" for x in data.get("glyphs", [])) +
                "\n"
            )

        elif game == "ob1":
            f.write(f"languageCode = {data.get('languageCode', 0)}\n")

        f.write("###\n\n")

        # ======================
        # OB1 FORMAT
        # ======================
        if game == "ob1":
            for e in data["entries"]:
                f.write("### ENTRY\n")
                f.write(f"index = {e['index']}\n")
                f.write(f"group = {e['group']}\n")
                f.write(f"id = {e['id']}\n")
                f.write(f"encoding = {e['encoding']}\n")

                if "param" in e:
                    f.write(f"param = {e['param']}\n")

                f.write("###\n")

                text = e.get("text", "")
                text = text.replace("\r", "\\r").replace("\n", "\\n")
                f.write(text + "\n\n")

        # ======================
        # FINAL EXAM FORMAT
        # ======================
        elif game == "finalexam":
            for e in data["entries"]:
                f.write("### ENTRY\n")
                f.write(f"index = {e['index']}\n")
                f.write(f"sid = 0x{e['sid']:08X}\n")
                f.write("###\n")

                for tag, text in e["subs"]:
                    text = text.replace("\r", "\\r").replace("\n", "\\n")
                    f.write(f"[tag=0x{tag:04X}] {text}\n")

                f.write("\n")