import struct

# ==========================================
# LÓGICA DE TRANSFORMAÇÃO DE TEXTO DO JOGO
# ===========================================
OB1_BUTTON_TAGS = [
    ("÷", "[L1]"),
    ("Æ", "[R1]"),
    ("Ð", "[Triangle]"),
    ("Ã", "[X]"),
    ("Ø", "[Select]"),
    ("Â", "[Circle]"),
    ("À", "[Square]"),
    ("Ç", "[R2]"),
    ("Å", "[Start]"),
    ("×︃", "[L2]"),
    ("Ê", "[L3]"),
    ("õ", "[R3]"),
]

def apply_ob1_tags(text):
    for src, tag in OB1_BUTTON_TAGS:
        text = text.replace(src, tag)
    return text

def reverse_ob1_tags(text):
    for src, tag in OB1_BUTTON_TAGS:
        text = text.replace(tag, src)
    return text

# ==============================
#     OBSCURE 1 (EXTRACT)
# ==============================  
def extract_ob1(path):
    import struct

    with open(path, "rb") as f:
        data = f.read()

    pos = 0

    def r_u32():
        nonlocal pos
        if pos + 4 > len(data):
            raise Exception(f"EOF u32 at {pos}")
        v = struct.unpack_from(">I", data, pos)[0]
        pos += 4
        return v

    def r_u16():
        nonlocal pos
        if pos + 2 > len(data):
            raise Exception(f"EOF u16 at {pos}")
        v = struct.unpack_from(">H", data, pos)[0]
        pos += 2
        return v

    language_code = r_u32()
    entry_count = r_u32()

    entries = []

    for i in range(entry_count):

        if pos + 9 > len(data):
            break  # evita crash hard

        group = r_u16()
        eid = r_u16()
        text_len = r_u32()

        if text_len < 1 or text_len > 0x10000:
            raise Exception(f"Invalid text_len {text_len} at {i}")

        enc = struct.unpack_from("<B", data, pos)[0]
        pos += 1

        param = None

        if enc == 1:
            param = struct.unpack_from("<B", data, pos)[0]
            pos += 1

        header_size = 1 + (1 if enc == 1 else 0)
        body_len = max(0, text_len - header_size)

        if pos + body_len > len(data):
            raise Exception(f"Overflow at entry {i}")

        raw = data[pos:pos + body_len]
        pos += body_len

        if enc == 0:
            text = apply_ob1_tags(
                raw.split(b"\x00")[0].decode("cp1252", errors="ignore")
            )
        else:
            text = raw.split(b"\x00\x00")[0].decode("utf-16le", errors="ignore")

        entries.append({
            "index": i,
            "group": group,
            "id": eid,
            "encoding": enc,
            "param": param or 0,
            "text": text
        })

    return {
        "game": "ob1",
        "languageCode": language_code,
        "entries": entries
    }

# ==============================
#     OBSCURE 1 (REBUILD)
# ==============================  
def rebuild_ob1(header, entries, out_path):
    import struct
    from io import BytesIO
    import os

    cp1252 = __import__("codecs").getencoder("cp1252")

    v = int(header.get("languageCode", 0))

    # ordena
    entries = sorted(
        entries,
        key=lambda e: int(e.get("index", 0))
    )

    fs = BytesIO()

    fs.write(struct.pack("<I", v))
    fs.write(struct.pack("<I", len(entries)))

    for e in entries:
        group = int(e["group"])
        eid = int(e["id"])
        enc = int(e["encoding"])
        param = int(e.get("param", 0))

        text = e["text"]

        fs.write(struct.pack("<H", group))
        fs.write(struct.pack("<H", eid))

        encoded = text.encode("cp1252", errors="ignore")

        text_len = 1 + len(encoded) + (1 if enc == 1 else 0)

        fs.write(struct.pack("<I", text_len))
        fs.write(struct.pack("<B", enc))

        if enc == 1:
            fs.write(struct.pack("<B", param))

        fs.write(encoded)

    base = out_path.replace(".new", "")
    base = os.path.splitext(base)[0]
    out = base + ".new.lng"

    with open(out, "wb") as f:
        f.write(fs.getvalue())

    return out