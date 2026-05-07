import struct
from io import BytesIO

# ==============================
#     FINAL EXAM (EXTRACT)
# ==============================      
def extract_final_exam(path):
    with open(path, "rb") as f:
        data = f.read()

    pos = 0

    def read_u32():
        nonlocal pos
        val = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        return val

    v1 = read_u32()
    magic = read_u32()
    total_subs = read_u32()
    entry_count = read_u32()
    glyph_count = read_u32()

    glyphs = [read_u32() for _ in range(glyph_count)]

    entries = []

    # ==============================
    # ENTRIES TABLE
    # ==============================
    raw_entries = []

    for i in range(entry_count):
        sid = read_u32()
        sub_count = read_u32()

        subs = []

        for _ in range(sub_count):
            a = read_u32()
            b = read_u32()

            offset = a & 0x1FFFF
            tag = a >> 17

            subs.append((tag, offset))

        raw_entries.append((sid, subs))

    # ==============================
    # STRING BLOCK
    # ==============================
    data_size = read_u32()
    str_data = data[pos:pos + data_size]

    def read_string(offset):
        end = str_data.find(b"\x00", offset)
        if end == -1:
            end = len(str_data)
        return str_data[offset:end].decode("utf-8", errors="replace")

    # ==============================
    # BUILD FINAL STRUCT
    # ==============================
    for i, (sid, subs) in enumerate(raw_entries):
        texts = []

        for tag, offset in subs:
            text = read_string(offset)
            texts.append((tag, text))

        entries.append({
            "index": i,
            "sid": sid,
            "subs": texts
        })

    return {
        "game": "finalexam",
        "v1": v1,
        "magic": magic,
        "glyphs": glyphs,
        "entries": entries
    }


# ==============================
#     FINAL EXAM (REBUILD)
# ==============================  
def rebuild_final_exam(header, entries, out_path):
    v1 = int(header.get("v1", 1))
    magic = int(header.get("magic", 0))

    glyphs = []
    glyph_str = header.get("glyphs", "").strip()

    if glyph_str:
        for g in glyph_str.split(","):
            g = g.strip()
            if g:
                glyphs.append(int(g, 16))

    data_stream = BytesIO()
    sub_records = []

    # ==============================
    # BUILD STRING TABLE
    # ==============================
    for e in sorted(entries, key=lambda x: int(x["index"])):
        sid = e["sid"]
        subs = e["subs"]

        converted = []

        for tag, text in subs:
            offset = data_stream.tell()

            data_stream.write(text.encode("utf-8", errors="replace"))
            data_stream.write(b"\x00")

            if offset > 0x1FFFF:
                raise Exception("Offset overflow (17-bit limit)")

            converted.append((tag, offset))

        sub_records.append((sid, converted))

    str_data = data_stream.getvalue()

    # ==============================
    # WRITE FILE
    # ==============================
    with open(out_path, "wb") as f:
        f.write(struct.pack("<I", v1))
        f.write(struct.pack("<I", magic))
        f.write(struct.pack("<I", sum(len(s[1]) for s in sub_records)))
        f.write(struct.pack("<I", len(sub_records)))
        f.write(struct.pack("<I", len(glyphs)))

        for g in glyphs:
            f.write(struct.pack("<I", g))

        for sid, subs in sub_records:
            f.write(struct.pack("<I", sid))
            f.write(struct.pack("<I", len(subs)))

            for tag, offset in subs:
                a = (tag << 17) | offset
                f.write(struct.pack("<I", a))
                f.write(struct.pack("<I", 0))

        f.write(struct.pack("<I", len(str_data)))
        f.write(str_data)

    return out_path