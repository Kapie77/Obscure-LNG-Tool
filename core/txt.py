# ==========================
#          .TXT
# ==========================

import unicodedata


# =====================
#        PARSE
# =====================
def parse_txt(content: str):
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    header = {}
    entries = []

    blocks = content.split("### ENTRY")

    # ======================
    # HEADER
    # ======================
    header_part = blocks[0] if blocks else ""

    for line in header_part.split("\n"):
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            header[k.strip().lower()] = v.strip()

    # ======================
    # GAME DETECTION (ROBUST)
    # ======================
    game_raw = header.get("game", "").strip().lower()

    if not game_raw:
        # fallback por estrutura
        if "[tag=" in content:
            game = "finalexam"
        elif "encoding" in content and "group =" in content:
            game = "ob1"
        elif "group_index" in content:
            game = "ob2"
        else:
            game = "ob1"
    else:
        if game_raw in ["ob2", "obscure2"]:
            game = "ob2"
        elif game_raw in ["ob1", "obscure1"]:
            game = "ob1"
        elif game_raw in ["finalexam", "final_exam"]:
            game = "finalexam"
        else:
            game = game_raw

    # ======================
    # ENTRIES
    # ======================
    for block in blocks[1:]:
        block = block.strip()
        if not block:
            continue

        meta_end = block.find("###")
        if meta_end == -1:
            continue

        meta = block[:meta_end].strip()
        body = block[meta_end + 3:].strip()

        body = body.replace("\\r", "\r").replace("\\n", "\n")

        # ======================
        # FINAL EXAM PARSER (FIX PRINCIPAL)
        # ======================
        if game == "finalexam":
            subs = []

            for line in body.split("\n"):
                line = line.strip()

                if not line:
                    continue

                if line.startswith("[tag="):
                    end = line.find("]")
                    if end == -1:
                        continue

                    tag_str = line[5:end]
                    text = line[end + 1:].strip()

                    try:
                        tag = int(tag_str, 16)
                    except:
                        tag = 0

                    text = text.replace("\\r", "\r").replace("\\n", "\n")

                    subs.append((tag, text))

            entry = {
                "index": 0,
                "sid": 0,
                "subs": subs
            }

        # ======================
        # OB2 STRUCT
        # ======================
        elif game == "ob2":
            entry = {
                "group_index": 0,
                "group_id": 0,
                "entry_index": 0,
                "meta": 0,
                "text": body
            }

        # ======================
        # OB1 STRUCT
        # ======================
        else:
            entry = {
                "index": 0,
                "group": 0,
                "id": 0,
                "encoding": 0,
                "param": 0,
                "text": body
            }

        # ======================
        # META PARSING
        # ======================
        for line in meta.split("\n"):
            line = line.strip()
            if "=" not in line:
                continue

            k, v = line.split("=", 1)
            k = k.strip().lower()
            v = v.strip()

            if game == "finalexam":
                if k == "index":
                    entry["index"] = int(v)
                elif k == "sid":
                    entry["sid"] = int(v, 16)

            elif game == "ob2":
                if k == "group_index":
                    entry["group_index"] = int(v)
                elif k == "group_id":
                    entry["group_id"] = int(v)
                elif k == "entry_index":
                    entry["entry_index"] = int(v)
                elif k == "meta":
                    entry["meta"] = int(v)

            else:
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

    return {
        "game": game,
        "header": header,
        "entries": entries
    }


# =====================
#       EXPORT
# =====================
def export_txt(data, path):
    # UTF-8 SEM BOM igual ao Obscure Text Editor
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

        # ======================
        # OB2 FORMAT
        # ======================
        elif game == "ob2":
            for e in data["entries"]:
                f.write("### ENTRY\n")
                f.write(f"group_index = {e['group_index']}\n")
                f.write(f"group_id = {e['group_id']}\n")
                f.write(f"entry_index = {e['entry_index']}\n")
                f.write(f"meta = {e['meta']}\n")
                f.write("###\n")

                text = e.get("text", "")
                text = text.replace("\r", "\\r").replace("\n", "\\n")

                f.write(text + "\n\n")