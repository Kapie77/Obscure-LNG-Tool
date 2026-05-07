import argparse
from core.detect import detect_game
from games.final_exam import extract_final_exam, rebuild_final_exam
from games.obscure1 import extract_ob1, rebuild_ob1
from core.txt import export_txt, parse_txt
from core.csv import export_csv, parse_csv

# ======================
#          CLI
# ======================
def main():
    parser = argparse.ArgumentParser(
        prog="lngtool",
        description="Final Exam / Obscure .lng tool"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # detect
    detect_cmd = sub.add_parser("detect")
    detect_cmd.add_argument("input")

    # extract
    extract_cmd = sub.add_parser("extract")
    extract_cmd.add_argument("input")
    extract_cmd.add_argument("-o", "--output")
    extract_cmd.add_argument("--format", choices=["txt", "csv", "both"], default="txt")

    # rebuild
    rebuild_cmd = sub.add_parser("rebuild")
    rebuild_cmd.add_argument("input")
    rebuild_cmd.add_argument("-o", "--output")

    args = parser.parse_args()

    # ======================
    # DETECT
    # ======================
    if args.command == "detect":
        print(detect_game(args.input))
        return

    # ======================
    # EXTRACT
    # ======================
    if args.command == "extract":
        game = detect_game(args.input)
        data = None

        if game == "finalexam":
            data = extract_final_exam(args.input)

        elif game == "ob1":
            data = extract_ob1(args.input)

        else:
            print(f"[ERRO] Detect failed. Game = {game}")
            return

        base = args.input.rsplit(".", 1)[0]

        if args.format in ["txt", "both"]:
            txt_out = args.output or base + ".txt"
            export_txt(data, txt_out)
            print(f"[OK] TXT → {txt_out}")

        if args.format in ["csv", "both"]:
            csv_out = base + ".csv"
            export_csv(data, csv_out)
            print(f"[OK] CSV → {csv_out}")

        return

    # ======================
    # REBUILD
    # ======================
    if args.command == "rebuild":

        base = args.input.rsplit(".", 1)[0]

        # ======================
        # TXT
        # ======================
        if args.input.endswith(".txt"):
            with open(args.input, encoding="utf-8") as f:
                data = parse_txt(f.read())

        # ======================
        # CSV
        # ======================
        elif args.input.endswith(".csv"):
            data = parse_csv(args.input)

        else:
            print("[ERRO] formato desconhecido")
            return

        header = data.get("header", {})
        entries = data.get("entries", [])
        game = data.get("game", "").lower()

        output = args.output or base + ".new.lng"

        if game in ["ob1", "obscure1"]:
            rebuild_ob1(header, entries, output)

        elif game in ["finalexam", "final_exam"]:
            rebuild_final_exam(header, entries, output)

        else:
            print(f"[ERRO] jogo desconhecido: {game}")


if __name__ == "__main__":
    main()