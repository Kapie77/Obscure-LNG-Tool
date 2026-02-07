#!/usr/bin/env python3
import struct
import csv
import argparse
import sys
import os
import unicodedata

# MAPAS DE SUBSTITUIÇÃO DE CARACTERES (se um caracter não funciona com acento vira uma letra normal, sem acento)
# OBSCURE 1
# Tabela de glifos da fonte do Obscure 1
# ABCDEFGIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/+-=.,;:!?"'*()[]||#\@&~^éèêçàâïîùûüôɛ¿¡áíóúñÁÉÍÓÚÑãõÃÕÜß$œ£¥©®™ìÈÌÒÙò

# font_holstein16
# font_lucida10(01234567889/)

MAP_OB1 = {
    # Maiúsculas acentuadas
    'Á': 'Á', 'À': 'A', 'Ã': 'A', 'Â': 'A',
    'É': 'É', 'Ê': 'E',
    'Í': 'Í',
    'Ó': 'Ó', 'Ô': 'O', 'Õ': 'O',
    'Ú': 'U',
    'Ç': 'C',
    'Ñ': 'N',
    'Œ': 'Œ',      # ligadura francesa
    'Ɇ': 'Ɇ',      # E com barra/traço do meio

    # Minúsculas acentuadas
    'á': 'á', 'à': 'à', 'â': 'â',
    'ã': 'a', 'é': 'é', 'ê': 'e',
    'í': 'í', 'ó': 'ó', 'ô': 'o', 'õ': 'o',
    'ú': 'u', 'ç': 'c', 'ñ': 'n',
    'œ': 'œ',      # ligadura francesa

    # Trema e diacríticos
    'Ä': 'Ä', 'Ë': 'E', 'Ï': 'I', 'Ö': 'Ö', 'Ü': 'Ü',
    'ä': 'ä', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',

    # Símbolos especiais da fonte
    '/': '/', '+': '+', '-': '-', '=': '=', '.': '.', ',': ',', ';': ';', ':': ':',
    '!': '!', '?': '?', '"': '"', "'": "'", '*': '*', '(': '(', ')': ')', '[': '[', ']': ']',
    '|': '|', '#': '#', '\\': '\\', '@': '@', '&': '&', '~': '~', '^': '^',
    '¿': '¿', '¡': '¡', '$': '$', '£': '£', '¥': '¥', '©': '©', '®': '®', '™': '™',
    'ì': 'ì', 'È': 'È', 'Ì': 'Ì', 'Ò': 'Ò', 'Ù': 'Ù', 'ò': 'ò'
}

# OBSCURE 2
# Tabela de glifos da fonte do Obscure 2
"""
Olhei as texturas do Obscure 2 e eis as fontes:
(manda o map consertado)

font_smallfonts7.tga:
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
/ + - = . , ; : ! ? " ' ° ( ) [ ] { } # \ @ & ~ ^
é è ê ç à â ï î ù û ü ô
œ ¿ ¡ á í ó ú ñ Á É Í Ó Ò Ú Ñ ä ö Ä Ö Ü ß $ €‎ £ ¥
© ® ™

font_arial14b.tga:
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
/ + - = . , ; : ! ? " ' ° ( ) [ ] { } # \ @ & ~ ^
é è ê ç à â ï î ù û

font_nonserif12.dds (a principal):
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
/ + - = . , ; : ! ? " ' ° ( ) [ ] { } # \ @ & ~ ^
é è ê ç à â ï î ù û ü ô
œ ¿ ¡ á í ó ú ñ 
Á É Í Ó Ò Ú Ñ ä ö Ä Ö Ü ß $ €‎ £ ¥
© ™ ì È Ì Ù ò < > (seta tipo < só que pra baixo) (seta tipo < que só pra cima) ®
# acelnoszzACELNOSZZ (todos esses com um ponto em cima, exceto o "a" "A" e o "e" "E" que tem traços embaixo tipo um cedilha, não sei o que seria isso; o z duplicado tem algo de diferente mas não consigo ver o que é)

font_mkabel12.dds:
0 1 2 3 4 5 6 7 8 9 / -

"""

MAP_OB2 = {
    # Glifos especiais da fonte (letras com ponto / traço estranho)
    'ȧ':'a','ċ':'c','ė':'e','l̇':'l','ṅ':'n','ȯ':'o','ṡ':'s','ż':'z',
    'Ȧ':'A','Ċ':'C','Ė':'E','L̇':'L','Ṅ':'N','Ȯ':'O','Ṡ':'S','Ż':'Z',
}

OB2_SUPPORTED = set(
    # Letras maiúsculas
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Letras minúsculas
    "abcdefghijklmnopqrstuvwxyz"

    # Números
    "0123456789"

    # Espaço
    " "

    # Pontuação e símbolos
    "/+-=.,;:!?\"'°()[]{}#\\@&~^"

    # Minúsculas acentuadas SUPORTADAS
    "éèêçàâïîùûüôœ¿¡áíóúñ"

    # Maiúsculas acentuadas SUPORTADAS
    "ÁÉÍÓÒÚÑÄÖÜß"

    # Outros símbolos presentes
    "$€£¥©®™ìÈÌÙò"

    # Setas especiais da font_nonserif12
    "<>"  # (as setas pra cima/baixo usam esses slots)
)


def normalize_for_ob2(text):
    out = []

    for c in text:
        # Se o jogo suporta, mantém
        if c in OB2_SUPPORTED:
            out.append(c)
            continue

        # Decompõe (NFD): õ → o + ~
        decomposed = unicodedata.normalize('NFD', c)

        # Remove diacríticos (combining marks)
        base = ''.join(
            ch for ch in decomposed
            if unicodedata.category(ch) != 'Mn'
        )

        # Se sobrou algo válido, usa
        if base and base[0] in OB2_SUPPORTED:
            out.append(base[0])
        else:
            # fallback final
            out.append('?')

    return ''.join(out)


# DETECTA QUAL O JOGO
def detect_game_type(lng_path):
    """Attempt to detect whether the file is from Obscure 1 or Obscure 2 based on first bytes"""
    try:
        with open(lng_path, 'rb') as f:
            magic = f.read(32)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if len(magic) < 16:
        return 'unknown'

    # Obscure 2: starts with languageCode + groupCount
    try:
        lang, groups = struct.unpack_from('<II', magic)
        # Relaxed check: languageCode pode ser maior (ex: 3844), groups razoável
        if groups >= 1 and groups <= 5000:  # limite alto para groupCount
            if len(magic) >= 16:
                group_id, entry_count = struct.unpack_from('<II', magic, 8)
                if 0 <= entry_count <= 20000:  # limite generoso para entryCount
                    return 'ob2'
    except:
        pass

    # Obscure 1: many leading zeros + no large groupCount early
    if magic[:4] == b'\x00\x00\x00\x00':
        # Avoid false positive if Obscure 2 has lang=0
        try:
            _, groups = struct.unpack_from('<II', magic)
            if groups > 5000 or groups == 0:
                return 'ob1'
        except:
            pass
        # Or readable text early after header
        if any(32 <= b <= 126 for b in magic[20:32]):
            return 'ob1'

    return 'unknown'


# EXTRAÇÃO DO OBSCURE 1
def extract_ob1(lng_path, prefix, encoding='latin-1', skip=28):
    with open(lng_path, 'rb') as f:
        data = f.read()

    content = data[skip:]

    entries = []
    pos = 0
    idx = 0

    MAX_STRINGS = 50000
    MAX_STRING_LEN = 8192
    NULL_RUN_LIMIT = 16
    null_run = 0

    while pos < len(content):
        if content[pos] == 0x00:
            null_run += 1
            if null_run >= NULL_RUN_LIMIT:
                break
            pos += 1
            continue
        else:
            null_run = 0

        end = content.find(b'\x00', pos)
        if end == -1:
            break

        size = end - pos
        if size > MAX_STRING_LEN:
            break

        raw = content[pos:end]

        # conta zeros após a string
        null_count = 0
        p = end
        while p < len(content) and content[p] == 0x00:
            null_count += 1
            p += 1

        text = raw.decode(encoding, errors='replace')

        entries.append({
            'index': idx,
            'offset': skip + pos,
            'max_len': size,
            'null_count': null_count,
            'original': text,
            'translated': ''
        })

        idx += 1
        pos = end + null_count

        if idx >= MAX_STRINGS:
            break

    csv_file = prefix + '.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['index', 'offset', 'max_len', 'null_count', 'original', 'translated']
        )
        writer.writeheader()
        writer.writerows(entries)

    print(f"✔ Obscure 1 - Extracted {len(entries)} strings")
    print(f"  Arquivo gerado: {csv_file}")


# EXTRAÇÃO DO OBSCURE 2
def extract_ob2(lng_path, prefix, format_type='both', encoding='utf-8'):
    """Extract Obscure 2 (languageCode + groups + meta + length + text)"""
    rows = []
    with open(lng_path, 'rb') as f:
        languageCode, groupCount = struct.unpack('<II', f.read(8))
        rows.append({
            'group_index': -1,
            'group_id': languageCode,
            'entry_index': -1,
            'meta': 0,
            'original': f"[Language Code: {languageCode}]",
            'translated': ''
        })

        for g in range(groupCount):
            groupId, entryCount = struct.unpack('<II', f.read(8))
            for e in range(entryCount):
                meta = struct.unpack('<I', f.read(4))[0]
                length = struct.unpack('<I', f.read(4))[0]
                text_bytes = f.read(length) if length > 0 else b''
                text = text_bytes.decode(encoding, errors='replace').rstrip('\x00')
                rows.append({
                    'group_index': g,
                    'group_id': groupId,
                    'entry_index': e,
                    'meta': meta,
                    'original': text,
                    'translated': ''
                })

    generated = []
    if format_type in ['txt', 'both']:
        txt_file = prefix + '.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            for row in rows:
                if row['group_index'] == -1:
                    f.write(f"Language Code: {row['group_id']}\n\n")
                else:
                    f.write(f"Group {row['group_index']:3d} | ID {row['group_id']:6d} | Entry {row['entry_index']:4d} | meta 0x{row['meta']:08X} | {row['original']}\n")
        generated.append(txt_file)

    if format_type in ['csv', 'both']:
        csv_file = prefix + '.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['group_index', 'group_id', 'entry_index', 'meta', 'original', 'translated']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        generated.append(csv_file)

    print(f"Obscure 2 - Extracted {len(rows)-1} entries (languageCode {languageCode})")
    print("Generated:", ", ".join(generated))
    return rows

# REPACK DO OBSCURE 1
def build_ob1(csv_path, original_lng, output_lng, encoding='latin-1'):
    with open(original_lng, 'rb') as f:
        data = bytearray(f.read())

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            offset = int(row['offset'])
            max_len = int(row['max_len'])
            null_count = int(row['null_count'])

            translated = row['translated'].strip()
            if not translated:
                continue  # NÃO TOCA NA STRING ORIGINAL

            # aplica o mapa
            translated = map_text(translated, 'ob1')

            encoded = translated.encode('cp1252', errors='replace') # IMPORTANTE: Obscure 1 usa encoding compatível com latin-1 / cp1252

            if len(encoded) > max_len:
                encoded = encoded[:max_len]

            data[offset:offset + len(encoded)] = encoded
            data[offset + len(encoded):offset + len(encoded) + null_count] = b'\x00' * null_count



    with open(output_lng, 'wb') as f:
        f.write(data)

    print(f"✔ Obscure 1 rebuilt → {output_lng}")
    print("  (tamanho do arquivo preservado)")


# REPACK DO OBSCURE 2
def build_ob2(csv_path, output_lng, encoding='utf-8', add_null=False):
    """Rebuild Obscure 2 from CSV"""
    groups = {}
    languageCode = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gidx = int(row['group_index'])
            if gidx == -1:
                languageCode = int(row['group_id'])
                continue
            gid = int(row['group_id'])
            eid = int(row['entry_index'])
            meta = int(row['meta'])
            text = row.get('translated', '').strip()
            if not text:
                text = row.get('original', '')
            groups.setdefault(gidx, {'gid': gid, 'entries': {}})
            groups[gidx]['entries'][eid] = (meta, text)

    groupCount = max(groups.keys(), default=-1) + 1

    with open(output_lng, 'wb') as f:
        f.write(struct.pack('<II', languageCode, groupCount))

        for g in range(groupCount):
            if g in groups:
                gid = groups[g]['gid']
                entries = groups[g]['entries']
                entryCount = max(entries.keys(), default=-1) + 1
            else:
                gid = 0
                entryCount = 0
                entries = {}

            f.write(struct.pack('<II', gid, entryCount))

            for e in range(entryCount):
                if e in entries:
                    meta, text = entries[e]
                    text = normalize_for_ob2(map_text(text, 'ob2'))  # aplica o mapa
                    btext = text.encode(encoding, errors='replace')  # codifica para bytes
                    if add_null and (not btext or btext[-1] != 0):
                        btext += b'\x00'
                    length = len(btext)
                else:
                    meta = 0
                    btext = b''
                    length = 0

                f.write(struct.pack('<II', meta, length))
                if length > 0:
                    f.write(btext)

    print(f"✔ Obscure 2 rebuilt → {output_lng}")
    print(f"  Grups: {groupCount}")


# FUNÇÃO DE NORMALIZAÇÃO COM MAPA
def map_text(text, game):
    if game == 'ob1':
        mapping = MAP_OB1
    elif game == 'ob2':
        mapping = MAP_OB2
    else:
        mapping = {}

    # Substitui apenas caracteres que estão no mapa
    return ''.join(mapping.get(c, c) for c in text)


# MAIN
def main():
    parser = argparse.ArgumentParser(
        description="Unified tool for Obscure 1 & 2 .lng files\n"
                    "Supports extraction to CSV/TXT and rebuilding to .lng\n\n"
                    "Obscure 1 (Extract):\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUE --game ob1 --format csv\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUE --game ob1 --format txt\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUE --game ob1 --format both\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob1 --format csv --encoding latin-1\n"
                    "\n"
                    "Obscure 1 (Repack/Build):\n"
                    "  python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob1 --original LANGUAGE.lng\n"
                    "\n"
                    "Obscure 2 (Extract):\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format csv\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format txt\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format both\n"
                    "  python obscure_lng_tool.py extract LANGUAGE.lng LANGUAGE --game ob2 --format csv --encoding utf-8\n"
                    "\n"
                    "Obscure 2 (Repack/Build):\n"
                    "  python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob2 --add-null",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    sub = parser.add_subparsers(dest='cmd', required=True, help='Available commands')

    # --- Extract ---
    ex = sub.add_parser(
        'extract',
        help='Extract .lng file into CSV and/or TXT',
        formatter_class=argparse.RawTextHelpFormatter
    )
    ex.add_argument('input', help='Input .lng file')
    ex.add_argument('prefix', help='Output prefix (e.g., my_dump)')
    ex.add_argument('--game', choices=['ob1', 'ob2'], required=True, help='Game type: ob1 or ob2')
    ex.add_argument('--format', '-f', choices=['csv', 'txt', 'both'], default='both',
                    help='Output format (default: both)')
    ex.add_argument('--skip', type=int, default=28, help='Bytes to skip (header) - only for ob1')
    ex.add_argument('--encoding', default=None, help='Text encoding (latin-1 for ob1, utf-8 for ob2)')

    # --- Build ---
    bu = sub.add_parser(
        'build',
        help='Rebuild .lng file from edited CSV',
        formatter_class=argparse.RawTextHelpFormatter
    )
    bu.add_argument('csv', help='Edited CSV file')
    bu.add_argument('output', help='Output .lng file')
    bu.add_argument('--game', choices=['ob1', 'ob2'], required=True, help='Game type: ob1 or ob2')
    bu.add_argument('--original', help='Original .lng file (required for ob1 to preserve header)')
    bu.add_argument('--add-null', action='store_true', help='Add \\x00 null terminator to strings')
    bu.add_argument('--encoding', default=None, help='Text encoding (latin-1 for ob1, utf-8 for ob2)')

    args = parser.parse_args()

    enc = args.encoding or ('latin-1' if args.game == 'ob1' else 'utf-8')

    if args.cmd == 'extract':
        detected = detect_game_type(args.input)

        if detected == 'unknown':
            print("⚠️ Could not automatically detect the .lng type.")
            print("Please specify --game ob1 or --game ob2 explicitly.")
        elif detected != args.game:
            print("\n" + "="*70)
            print("❌ ERROR: Selected game does not match detected file type!")
            print(f"  Detected: {detected.upper()}")
            print(f"  You selected: --game {args.game}")
            print("="*70 + "\n")
            sys.exit(1)

        if args.game == 'ob1':
            extract_ob1(args.input, args.prefix, enc, args.skip)
        else:
            extract_ob2(args.input, args.prefix, args.format, enc)

    elif args.cmd == 'build':
        if args.game == 'ob1' and not args.original:
            parser.error("--original is required for Obscure 1 (to preserve header)")

        if args.game == 'ob1':
            build_ob1(args.csv, args.original, args.output, enc)
        else:
            build_ob2(args.csv, args.output, enc, args.add_null)


# FUNÇÃO DE ARRASTAR E SOLTAR
def main_drag_drop():
    if len(sys.argv) < 2:
        print("Drag and drop a .lng or .csv/.txt file onto this program.")
        return

    for path in sys.argv[1:]:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue

        ext = os.path.splitext(path)[1].lower()

        if ext == '.lng':
            # Detecta o jogo
            game = detect_game_type(path)
            if game == 'unknown':
                print(f"{path}: Não foi possível detectar o tipo de jogo. Usando ob1 como padrão.")
                game = 'ob1'

            prefix = os.path.splitext(path)[0]
            if game == 'ob1':
                extract_ob1(path, prefix, encoding='latin-1', skip=28)
            else:
                extract_ob2(path, prefix, format_type='csv', encoding='utf-8')

        elif ext in ('.csv', '.txt'):
            base = os.path.splitext(path)[0]
            original_lng = base + '.lng'
            output_lng = base + '_new.lng'

            if os.path.exists(original_lng):
                game = detect_game_type(original_lng)
            else:
                print(f"⚠️ Arquivo .lng original não encontrado para detectar o jogo:")
                print(f"   Esperado: {original_lng}")
                print("   Usando Obscure 1 como padrão.")
                game = 'ob1'

            if game == 'ob1':
                if not os.path.exists(original_lng):
                    print(f"❌ Obscure 1 precisa do .lng original para rebuild.")
                    continue
                build_ob1(path, original_lng, output_lng)
            elif game == 'ob2':
                build_ob2(path, output_lng, encoding='utf-8')
            else:
                print(f"❌ Não foi possível detectar o tipo do jogo para: {path}")


        else:
            print(f"Formato não suportado: {path}")

# Detecta se o programa foi aberto via arrastar e soltar ou via linha de código
if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Nenhum argumento: provavelmente double-click sem arquivo → mostra ajuda
        main()
    elif len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        # Arrastou apenas 1 arquivo → drag & drop
        main_drag_drop()
    else:
        # Passou argumentos → CLI normal

        main()

