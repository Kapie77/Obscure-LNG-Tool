# ==========================
#          .TXT
# ==========================
def parse_txt(content: str):
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    header = {}
    entries = []

    first_entry_idx = content.find("### ENTRY")

    if first_entry_idx == -1:
        lang_part = content
        rest = ""
    else:
        lang_part = content[:first_entry_idx]
        rest = content[first_entry_idx:]

    # HEADER
    for line in lang_part.split("\n"):
        l = line.strip()
        if not l or l.startswith("###"):
            continue
        if "=" in l:
            k, v = l.split("=", 1)
            header[k.strip()] = v.strip()

    # ENTRIES
    sections = rest.split("### ENTRY")

    for sec in sections:
        if not sec.strip():
            continue

        close_idx = sec.find("###")
        if close_idx == -1:
            continue

        header_part = sec[:close_idx]
        body_part = sec[close_idx + 3:]

        entry_header = {}
        for line in header_part.split("\n"):
            l = line.strip()
            if "=" in l:
                k, v = l.split("=", 1)
                entry_header[k.strip()] = v.strip()

        # 🔥 CONVERTE DIRETO PARA SUBS
        subs = []

        for line in body_part.split("\n"):
            line = line.strip()
            if not line.startswith("[tag="):
                continue

            end = line.find("]")
            tag = int(line[5:end], 16)
            text = line[end + 1:].strip()

            text = text.replace("\\n", "\n").replace("\\r", "\r")

            subs.append((tag, text))

        entries.append({
            "index": int(entry_header["index"]),
            "sid": int(entry_header["sid"], 16),
            "subs": subs
        })

    return header, entries


def export_txt(data, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("### LANGUAGE\n")
        f.write("game = finalexam\n")
        f.write(f"v1 = {data['v1']}\n")
        f.write(f"magic = 0x{data['magic']:08X}\n")

        glyphs = ",".join(f"0x{g:X}" for g in data["glyphs"])
        f.write(f"glyphs = {glyphs}\n")
        f.write("###\n\n")

        for entry in data["entries"]:
            f.write("### ENTRY\n")
            f.write(f"index = {entry['index']}\n")
            f.write(f"sid = 0x{entry['sid']:08X}\n")
            f.write("###\n")

            for tag, text in entry["subs"]:
                text = text.replace("\n", "\\n").replace("\r", "\\r")
                f.write(f"[tag=0x{tag:04X}] {text}\n")

            f.write("\n")