# ==========================================================
#      DETECT GAME (ObsCure 1, ObsCure 2 or Final Exam)
# ==========================================================
import struct

def detect_game(path):
    with open(path, "rb") as f:
        data = f.read(16)

    if len(data) < 8:
        return "unknown"

    a_le, b_le = struct.unpack("<II", data[:8])
    a_be, b_be = struct.unpack(">II", data[:8])

    # =====================
    # FINAL EXAM
    # =====================
    if a_le == 1 and (b_le & 0xFF00FFFF) == 0x01000000:
        return "finalexam"

    # =====================
    # OBSCURE 1
    # =====================
    if a_be == 0 and 1 <= b_be <= 200000:
        return "ob1"

    # =====================
    # OBSCURE 2
    # =====================
    # heuristic extra: languageCode + groupCount sanity
    if 1 <= b_le <= 200000 and a_le < 10000:
        return "ob2"

    return "unknown"