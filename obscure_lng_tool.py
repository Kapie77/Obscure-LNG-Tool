import sys
import argparse
from core.detect import detect_game
from games.final_exam import extract_final_exam, rebuild_final_exam
from games.obscure1 import extract_ob1, rebuild_ob1
from games.obscure2 import extract_ob2, rebuild_ob2
from core.txt import export_txt, parse_txt
from core.csv import export_csv, parse_csv

# ======================
#          CLI
# ======================
def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        prog="lngtool",
        description="Obscure 1, Obscure 2 and Final Exam .lng tool"
    )

    sub = parser.add_subparsers(dest="command")

    detect_cmd = sub.add_parser("detect")
    detect_cmd.add_argument("input")

    extract_cmd = sub.add_parser("extract")
    extract_cmd.add_argument("input")
    extract_cmd.add_argument("-o", "--output")
    extract_cmd.add_argument("--format", choices=["txt", "csv", "both"], default="txt")

    rebuild_cmd = sub.add_parser("rebuild")
    rebuild_cmd.add_argument("input")
    rebuild_cmd.add_argument("-o", "--output")

    # ======================
    # DRAG & DROP SUPPORT
    # ======================
    if len(sys.argv) == 2 and not sys.argv[1].startswith("-"):
        file_path = sys.argv[1].strip('"')

        # ======================
        # EXTRACT (.lng)
        # ======================
        if file_path.endswith(".lng"):
            print("\nChoose output format:")
            print("[1] TXT")
            print("[2] CSV")
            print("[3] BOTH")
            print("Or type: txt / csv / both\n")

            choice = input("Option: ").strip().lower()

            if choice in ["1", "txt"]:
                fmt = "txt"
            elif choice in ["2", "csv"]:
                fmt = "csv"
            elif choice in ["3", "both"]:
                fmt = "both"
            else:
                print("[ERRO] invalid option")
                sys.exit(1)

            args = argparse.Namespace(
                command="extract",
                input=file_path,
                output=None,
                format=fmt
            )

        # ======================
        # REBUILD (.txt / .csv)
        # ======================
        elif file_path.endswith((".txt", ".csv")):
            args = argparse.Namespace(
                command="rebuild",
                input=file_path,
                output=None
            )

        else:
            print("[ERRO] unknown file type:", file_path)
            sys.exit(1)
    else:
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

        elif game == "ob2":
            data = extract_ob2(args.input)   # <<<<<< FALTAVA ISSO

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

        if args.input.endswith(".txt"):
            with open(args.input, encoding="utf-8") as f:
                data = parse_txt(f.read())

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
            print(f"[OK] OB1 rebuild → {output}")

        elif game in ["finalexam", "final_exam"]:
            rebuild_final_exam(header, entries, output)
            print(f"[OK] FINAL EXAM rebuild → {output}")

        elif game in ["ob2", "obscure2"]:
            rebuild_ob2(header, entries, output)
            print(f"[OK] OB2 rebuild → {output}")

        else:
            print(f"[ERRO] jogo desconhecido: {game}")


if __name__ == "__main__":
    main()