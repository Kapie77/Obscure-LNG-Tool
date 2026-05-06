import argparse
from core.detect import detect_game
from games.final_exam import extract_final_exam, rebuild_final_exam
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
    detect_cmd = sub.add_parser("detect", help="Detect game type")
    detect_cmd.add_argument("input")

    # extract .txt
    extract_cmd = sub.add_parser("extract", help="Extract .lng to .txt")
    extract_cmd.add_argument("input")
    extract_cmd.add_argument("-o", "--output")

    # extract .csv
    extract_cmd.add_argument(
        "--format",
        choices=["txt", "csv", "both"],
        default="txt"
    )

    # rebuild
    rebuild_cmd = sub.add_parser("rebuild", help="Rebuild .lng from .txt")
    rebuild_cmd.add_argument("input")
    rebuild_cmd.add_argument("-o", "--output")

    args = parser.parse_args()

    if args.command == "detect":
        game = detect_game(args.input)
        print(game)
        return

    # Extract
    if args.command == "extract":
        game = detect_game(args.input)

        if game in ["final_exam", "finalexam"]:
            data = extract_final_exam(args.input)

            base = args.input.rsplit(".", 1)[0]

            # TXT
            if args.format in ["txt", "both"]:
                txt_out = args.output or base + ".txt"
                export_txt(data, txt_out)
                print(f"[OK] TXT → {txt_out}")

            # CSV
            if args.format in ["csv", "both"]:
                csv_out = base + ".csv"
                export_csv(data, csv_out)
                print(f"[OK] CSV → {csv_out}")
        else:
            print(f"[ERRO] Jogo não suportado: {game}")
        return

    # Rebuild
    if args.command == "rebuild":
        if not args.output:
            args.output = args.input.rsplit(".", 1)[0] + ".new.lng"

        # CSV
        if args.input.endswith(".csv"):
            entries = parse_csv(args.input)

            header = {
                "v1": "1",
                "magic": "0x01400000",
                "game": "finalexam",
                "glyphs": ""
            }

        # TXT
        else:
            with open(args.input, encoding="utf-8") as f:
                header, entries = parse_txt(f.read())

        game = header.get("game", "").lower()

        if game in ["finalexam", "final_exam"]:
            output = rebuild_final_exam(header, entries, args.output)
            print(f"[OK] Rebuilt → {output}")
        else:
            print(f"[ERRO] Jogo não suportado no input: {game}")
        return


if __name__ == "__main__":
    main()