# ==========================================================
#      DETECT GAME (ObsCure 1, ObsCure 2 or Final Exam)
# ==========================================================
import struct

def detect_game(path):
    with open(path, "rb") as f:
        data = f.read(8)

    if len(data) < 8:
        return "unknown"

    a_le, b_le = struct.unpack("<II", data)

    if a_le == 1 and (b_le & 0xFF00FFFF) == 0x01000000:
        return "final_exam"

    return "unknown"