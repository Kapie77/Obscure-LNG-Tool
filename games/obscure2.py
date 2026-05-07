import struct

CP1252 = "cp1252"


# =========================
#     SMART DECODER
# =========================
def smart_decode(raw: bytes) -> str:
    """
    Obscure 2 usa mistura de CP1252 e UTF-8 em algumas entradas.
    O editor oficial aparentemente tolera ambos.
    """

    raw = raw.split(b"\x00")[0]

    # tenta UTF-8 primeiro (corrige casos tipo C3 88 = È)
    try:
        text = raw.decode("utf-8")
        if "�" not in text:
            return text
    except UnicodeDecodeError:
        pass

    # fallback CP1252
    return raw.decode(CP1252, errors="replace")


# =========================
#        EXTRACT
# =========================
def extract_ob2(path):
    with open(path, "rb") as f:
        data = f.read()

    pos = 0

    def u32():
        nonlocal pos
        v = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        return v

    languageCode = u32()
    groupCount = u32()

    entries = []

    for g in range(groupCount):
        groupId = u32()
        entryCount = u32()

        for e in range(entryCount):
            meta = u32()
            length = u32()

            text = ""

            if length > 0 and pos + length <= len(data):
                raw = data[pos:pos + length]
                pos += length

                # 🔥 FIX PRINCIPAL: decoder híbrido
                text = smart_decode(raw)

            else:
                pos += length

            entries.append({
                "group_index": g,
                "group_id": groupId,
                "entry_index": e,
                "meta": meta,
                "text": text
            })

    return {
        "game": "ob2",
        "languageCode": languageCode,
        "entries": entries
    }


# =========================
#        REBUILD
# =========================
def rebuild_ob2(header, entries, out_path):
    languageCode = int(header.get("languageCode", 0))

    groups = {}

    for e in entries:
        g = int(e["group_index"])

        if g not in groups:
            groups[g] = {
                "group_id": int(e["group_id"]),
                "entries": {}
            }

        groups[g]["entries"][int(e["entry_index"])] = e

    with open(out_path, "wb") as f:
        f.write(struct.pack("<I", languageCode))
        f.write(struct.pack("<I", len(groups)))

        for g in sorted(groups.keys()):
            group = groups[g]
            f.write(struct.pack("<I", group["group_id"]))

            entry_dict = group["entries"]
            max_e = max(entry_dict.keys()) if entry_dict else -1

            f.write(struct.pack("<I", max_e + 1))

            for i in range(max_e + 1):
                if i in entry_dict:
                    e = entry_dict[i]
                    meta = int(e["meta"])

                    # 🔥 FIX: mantém comportamento do editor (CP1252 tolerante)
                    text_bytes = e["text"].encode("cp1252", errors="replace")
                else:
                    meta = 0
                    text_bytes = b""

                f.write(struct.pack("<I", meta))
                f.write(struct.pack("<I", len(text_bytes)))
                f.write(text_bytes)