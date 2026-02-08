#!/usr/bin/env python3
import struct
import csv
import argparse
import sys
import os
import unicodedata
import re

# MAPAS DE SUBSTITUIÇÃO DE CARACTERES (se um caracter não funciona com acento vira uma letra normal, sem acento)
# OBSCURE 1
# Tabela de glifos da fonte do Obscure 1
"""
font_holstein16 (principal)
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
/ + - = . , ; : ! ? " ' ° ( ) [ ] { } # \ @ & ~ ^
é è ê ç à â ï î ù û ü ô
œ ¿ ¡ á í ó ú ñ Á É Í Ó Ú Ñ ä ö Ä Ö Ü ß $ €‎ £ ¥
© ® ™
ì È Ì Ò Ù

font_lucida10
0 1 2 3 4 5 6 7 8 9 /

font_holstein18
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
é è ê ç à â ï î ù û ü ô
, ' : ! ? . ( ) [ ] / @ + (quadrado) = " $ (quadrado)

font_holstein24
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
0 1 2 3 4 5 6 7 8 9
/ + - = . , ; : ! ? " ' ° ( ) [ ] # \ ¿ ¡
Á É Í Ó Ú Ñ Ä Ö Ü ß
© ® ™

font_holstein30
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
/ - . , ; : ! ? " ' ° ( ) [ ] # \ ¿ ¡
Á É Í Ó Ú Ñ Ä Ö Ü ß
"""

MAP_OB1 = {
   # Glifos especiais da fonte (letras com ponto / traço estranho)
    'ȧ':'a','ċ':'c','ė':'e','l̇':'l','ṅ':'n','ȯ':'o','ṡ':'s','ż':'z',
    'Ȧ':'A','Ċ':'C','Ė':'E','L̇':'L','Ṅ':'N','Ȯ':'O','Ṡ':'S','Ż':'Z',

    'Æ':'A', 'æ':'a',
    'Œ':'O', 'œ':'o',
    'ò':'o', 'Ò':'O',
    'õ':'o', 'Õ':'O',
}

OB1_SUPPORTED = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"      # Maiúsculas
    "abcdefghijklmnopqrstuvwxyz"      # Minúsculas
    "0123456789"                      # Números
    " "                               # Espaço
    "/+-=.,;:!?\"'°()[]{}#\\@&~^"     # Símbolos da fonte
    "éèêçàâïîùûüô"                    # Minúsculas acentuadas
    "áíóúñÁÉÍÓÚÑÄÖÜß"                 # Maiúsculas acentuadas
    "$€£¥©®™"                         # Outros símbolos especiais
)

def normalize_for_ob1(text):
    out = []

    for c in text:
        # Suportado direto
        if c in OB1_SUPPORTED:
            out.append(c)
            continue

        # Mapa manual
        if c in MAP_OB1:
            out.append(MAP_OB1[c])
            continue

        # Decomposição Unicode (Õ → O + ~)
        decomposed = unicodedata.normalize('NFD', c)
        base = ''.join(
            ch for ch in decomposed
            if unicodedata.category(ch) != 'Mn'
        )

        # Se a letra base existir na fonte, usa
        if base and base[0] in OB1_SUPPORTED:
            out.append(base[0])
        else:
            # último fallback REALISTA
            out.append('')

    return ''.join(out)

# Ignora bytes que não são glifos
def clean_ob1_text(raw_bytes):
    """
    Remove tokens de controle do Obscure 1.
    Mantém SOMENTE bytes que mapeiam para glifos reais da fonte.
    """
    clean = bytearray()

    for b in raw_bytes:
        # ASCII imprimível básico (espaço até ~)
        if 0x20 <= b <= 0x7E:
            clean.append(b)
            continue

        # Acentos CP1252 usados pela fonte Holstein
        if b in (
            0xE9, 0xE8, 0xEA, 0xE7, 0xE0, 0xE2,
            0xEF, 0xEE, 0xF9, 0xFB, 0xFC, 0xF4,
            0xE1, 0xED, 0xF3, 0xFA, 0xF1,
            0xC1, 0xC9, 0xCD, 0xD3, 0xDA, 0xD1,
            0x99,  # ™
            0xA9,  # ©
            0xAE,  # ®
        ):
            clean.append(b)
            continue

        # Qualquer outro byte é TOKEN → IGNORA
        continue

    return bytes(clean)

# limpza final do texto do ob1
def extract_ob1_label(text):
    """
    Extrai apenas o LABEL do Obscure 1 (menus).
    Remove textos de ajuda, input hints, etc.
    """

    # caso simples: tudo ALL CAPS (ok)
    if re.fullmatch(r'[A-Z0-9 ]+', text):
        return text

    # corta quando começa texto explicativo
    m = re.match(r'^([A-Z0-9 ]+)', text)
    if m:
        return m.group(1)

    return text



# OBSCURE 2
# Tabela de glifos da fonte do Obscure 2
"""
font_smallfonts7.tga:
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
'/ + - = . , ; : ! ? " \' ° ( ) [ ] { } # \\ @ & ~ ^'
é è ê ç à â ï î ù û ü ô
œ ¿ ¡ á í ó ú ñ Á É Í Ó Ò Ú Ñ ä ö Ä Ö Ü ß $ €‎ £ ¥
© ® ™

font_arial14b.tga:
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
'/ + - = . , ; : ! ? " \' ° ( ) [ ] { } # \\ @ & ~ ^'
é è ê ç à â ï î ù û

font_nonserif12.dds (a principal):
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
'/ + - = . , ; : ! ? " \' ° ( ) [ ] { } # \\ @ & ~ ^'
é è ê ç à â ï î ù û ü ô
œ ¿ ¡ á í ó ú ñ 
Á É Í Ó Ò Ú Ñ ä ö Ä Ö Ü ß $ €‎ £ ¥
© ™ ì È Ì Ù ò < > V Λ ®
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
    try:
        with open(lng_path, 'rb') as f:
            head = f.read(16)

        if len(head) < 8:
            return 'unknown'

        a, b = struct.unpack('>II', head[:8])

        # Obscure 1: entryCount grande, grupos pequenos depois
        if a == 0 and 1 <= b <= 100000:
            return 'ob1'

        # Obscure 2: languageCode != 0, poucos grupos
        if a != 0 and 1 <= b <= 10000:
            return 'ob2'

    except Exception:
        pass

    return 'unknown'

# Ler byte-a-byte até encontrar um terminador real Obscure 1
def read_ob1_string(f, max_len=4096):
    buf = bytearray()
    read_bytes = 0

    while read_bytes < max_len:
        b = f.read(1)
        if not b:
            break

        b = b[0]
        read_bytes += 1

        # terminadores fortes
        if b == 0x00:
            break

        # quebra de linha inesperada em label
        if b in (0x0A, 0x0D):
            break

        buf.append(b)

    return bytes(buf), read_bytes


# EXTRAÇÃO DO OBSCURE 1
def extract_ob1(lng_path, prefix, encoding='cp1252'):
    rows = []

    with open(lng_path, 'rb') as f:
        # 🔎 Procura header válido (0, entryCount)
        header_pos = None
        entryCount = None

        f.seek(0, 2)
        file_size = f.tell()  # tamanho total do arquivo

        for offset in range(0, file_size - 8, 4):  # percorre TODO o arquivo
            f.seek(offset)
            buf = f.read(8)
            if len(buf) < 8:
                continue
            a, b = struct.unpack('>II', buf)
            if a == 0 and 1 <= b <= 100000:
                header_pos = offset
                entryCount = b

                meta = {
                    'header_pos': header_pos,
                    'entryCount': entryCount
                }

                import json

                with open(prefix + '.meta.json', 'w', encoding='utf-8') as mf:
                    json.dump(meta, mf, indent=2)


                break

        if header_pos is None:
            print("❌ Could not find valid Obscure 1 header.")
            return


        # Vai para o começo real das entries
        f.seek(header_pos + 8)

        for i in range(entryCount):
            header = f.read(4)
            if len(header) < 4:
                print(f"⚠️ Unexpected EOF while reading entry {i}")
                break

            group, eid = struct.unpack('>HH', header)

            buf = f.read(4)
            if len(buf) < 4:
                print(f"⚠️ Unexpected EOF when reading textLen from entry {i}")
                break

            textLen = struct.unpack('>I', buf)[0]

            # SANITY CHECK
            if textLen <= 0 or textLen > 4096:
                print(f"⚠️ Invalid textLen ({textLen}) in entry {i}, aborting extraction OB1.")
                continue

            enc = struct.unpack('B', f.read(1))[0]  # 1 byte não depende de endian

            data_len = textLen - 1
            param = None

            if enc == 1:
                p = f.read(1)
                if len(p) < 1:
                    print(f"⚠️ Unexpected EOF when reading entry param {i}")
                    break
                param = struct.unpack('B', p)[0]
                data_len -= 1

            data, consumed = read_ob1_string(f, textLen)
            clean = clean_ob1_text(data)

            # pula o resto do bloco, se sobrar
            remaining = data_len - consumed
            if remaining > 0:
                f.seek(remaining, 1)


            try:
                text = clean.decode(encoding, errors='replace')
                text = extract_ob1_label(text)
            except Exception:
                text = ''


            rows.append({
                'index': i,
                'group': group,
                'id': eid,
                'encoding': enc,
                'param': param if param is not None else '',
                'textLen': textLen,
                'original': text,
                'translated': ''
            })

    csv_file = prefix + '.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['index', 'group', 'id', 'encoding', 'param', 'textLen', 'original', 'translated']
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✔ Obscure 1 - Extracted {len(rows)} entries")



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

# validação de placehodlers do obscure 1
def extract_placeholders(text):
    return re.findall(r'%[sdif]', text)

# REPACK DO OBSCURE 1
def build_ob1(csv_path, output_lng, encoding='cp1252'):
    import json

    meta_path = os.path.splitext(csv_path)[0] + '.meta.json'
    if not os.path.exists(meta_path):
        raise RuntimeError(".meta.json file not found")

    with open(meta_path, 'r', encoding='utf-8') as mf:
        meta = json.load(mf)

    entryCount = meta['entryCount']
    header_pos = meta.get('header_pos', 0)

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # valida ordem e quantidade
    rows.sort(key=lambda r: int(r['index']))

    if len(rows) != entryCount:
        raise ValueError(
            f"CSV has {len(rows)} entries, but the header expects {entryCount}"
        )
    
    for expected, row in enumerate(rows):
        if int(row['index']) != expected:
            raise ValueError(
                f"Index out of order or missing: expected {expected}, found {row[‘index’]}"
            )

    with open(output_lng, 'wb') as f:
        # padding até o header original
        if header_pos > 0:
            f.write(b'\x00' * header_pos)

        # HEADER ORIGINAL NO OFFSET CORRETO
        f.write(struct.pack('>II', 0, entryCount))

        for row in rows:
            group = int(row['group'])
            eid   = int(row['id'])
            enc   = int(row['encoding'])
            param = int(row['param']) if row['param'] else None

            text = row['translated'] or row['original']

            # NORMALIZAÇÃO
            text = normalize_for_ob1(text)  # Aplica mapa + validação de caracteres suportados

            # VALIDAÇÃO DE PLACEHOLDERS (APENAS encoding == 1)
            if enc == 1:
                orig_ph = extract_placeholders(row['original'])
                new_ph  = extract_placeholders(text)

                if orig_ph != new_ph:
                    raise ValueError(
                        f"Incompatible placeholders in entry {row[‘index’]}: "
                        f"{orig_ph} != {new_ph}"
                    )

            data = text.encode('cp1252', errors='replace')

            orig_textLen = int(row['textLen'])

            # converte para bytes
            text_bytes = text.encode('cp1252', errors='replace')

            # calcula textLen corretamente
            if enc == 0:
                textLen = 1 + len(text_bytes)      # 1 byte encoding + texto
            elif enc == 1:
                textLen = 1 + 1 + len(text_bytes)  # 1 byte encoding + 1 byte param + texto


            # ESCREVE ENTRY
            f.write(struct.pack('>HHI', group, eid, textLen))
            f.write(struct.pack('B', enc))

            if enc == 1:
                f.write(struct.pack('B', param))
            
            # escreve os bytes do texto
            f.write(text_bytes)


    print(f"✔ Obscure 1 rebuilt → {output_lng}")


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
    print(f"  Groups: {groupCount}")


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
                    "  python obscure_lng_tool.py build LANGUAGE.csv LANGUAGE.new.lng --game ob1 LANGUAGE.lng\n"
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
    bu.add_argument('--add-null', action='store_true', help='Add \\x00 null terminator to strings')
    bu.add_argument('--encoding', default=None, help='Text encoding (latin-1 for ob1, utf-8 for ob2)')

    args = parser.parse_args()

    enc = args.encoding or ('cp1252' if args.game == 'ob1' else 'utf-8')

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
            extract_ob1(args.input, args.prefix, enc)
        else:
            extract_ob2(args.input, args.prefix, args.format, enc)

    elif args.cmd == 'build':

        if args.game == 'ob1':
            build_ob1(args.csv, args.output, enc)
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
                print(f"❌ {path}: The type of .lng could not be detected.")
                print("    Use the command line and specify --game ob1 or ob2.")
                continue

            prefix = os.path.splitext(path)[0]
            if game == 'ob1':
                extract_ob1(path, prefix, encoding='cp1252')
            else:
                extract_ob2(path, prefix, format_type='csv', encoding='utf-8')

        elif ext in ('.csv', '.txt'):
            base = os.path.splitext(path)[0]
            original_lng = base + '.lng'
            output_lng = base + '_new.lng'

            if os.path.exists(original_lng):
                game = detect_game_type(original_lng)
            else:
                print(f"⚠️ Original .lng file not found to detect the game:")
                print(f"   Esperado: {original_lng}")
                print("   Using Obscure 1 as the default.")
                game = 'ob1'

            if game == 'ob1':
                build_ob1(path, output_lng, encoding='cp1252')
            elif game == 'ob2':
                build_ob2(path, output_lng, encoding='utf-8')
            else:
                print(f"❌ Unable to detect the game type for: {path}")


        else:
            print(f"Unsupported format: {path}")

            if os.name == 'nt':
                input("\nPress ENTER to exit...")


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