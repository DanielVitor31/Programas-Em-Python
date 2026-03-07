NOME_PROGRAMA = "Editar INSERT SQL"
DESC_PROGRAMA = "Remove colunas escolhidas"

import sys
import re
import subprocess


def set_clipboard(text: str) -> None:
    # Windows clipboard via PowerShell (sem tkinter / sem pip)
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
        input=text,
        text=True,
        check=True
    )


def read_insert_multiline() -> str:
    print("\nCole o INSERT inteiro agora.")
    print("IMPORTANTE: finalize com Ctrl+Z e depois Enter.\n")
    return sys.stdin.read()


def extract_insert_parts(sql: str):
    """
    Retorna (tabela, colunas_texto, values_texto).
    """
    sql = sql.strip()
    has_semicolon = sql.rstrip().endswith(";")
    if has_semicolon:
        sql = sql.rstrip()[:-1]

    m = re.search(
        r"insert\s+into\s+(?P<table>[\w\.]+)\s*\((?P<cols>[^)]+)\)\s*values\s*(?P<vals>.+)$",
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )
    if not m:
        raise ValueError("INSERT inválido (esperado: INSERT INTO ... (colunas) VALUES ...).")

    return m.group("table"), m.group("cols"), m.group("vals"), has_semicolon


def split_top_level_commas(s: str) -> list[str]:
    """
    Split por vírgula apenas quando:
      - fora de aspas simples
      - fora de parênteses
    Suporta escape SQL '' dentro de strings.
    """
    out = []
    buf = []
    in_quote = False
    depth = 0
    i = 0

    while i < len(s):
        ch = s[i]

        if ch == "'":
            if in_quote and i + 1 < len(s) and s[i + 1] == "'":
                buf.append("''")
                i += 2
                continue
            in_quote = not in_quote
            buf.append(ch)
            i += 1
            continue

        if not in_quote:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif ch == "," and depth == 0:
                out.append("".join(buf).strip())
                buf = []
                i += 1
                continue

        buf.append(ch)
        i += 1

    out.append("".join(buf).strip())
    return out


def extract_value_tuples(values_text: str) -> list[str]:
    """
    Extrai tuplas top-level: ( ... ), ( ... ), ...
    Respeita aspas.
    """
    tuples = []
    in_quote = False
    depth = 0
    start = None
    i = 0

    while i < len(values_text):
        ch = values_text[i]

        if ch == "'":
            if in_quote and i + 1 < len(values_text) and values_text[i + 1] == "'":
                i += 2
                continue
            in_quote = not in_quote
            i += 1
            continue

        if not in_quote:
            if ch == "(":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and start is not None:
                    tuples.append(values_text[start:i + 1])
                    start = None

        i += 1

    return tuples


def process(sql: str, cols_to_remove_csv: str) -> str:
    table, cols_text, vals_text, had_semicolon = extract_insert_parts(sql)

    remove_set = {c.strip().lower() for c in cols_to_remove_csv.split(",") if c.strip()}
    cols = [c.strip() for c in cols_text.split(",")]

    keep_idx = [i for i, c in enumerate(cols) if c.lower() not in remove_set]
    if not keep_idx:
        raise ValueError("Você removeu todas as colunas. Aí não rola.")

    new_cols = [cols[i] for i in keep_idx]

    tuples = extract_value_tuples(vals_text)
    if not tuples:
        raise ValueError("Não encontrei tuplas (...) em VALUES.")

    new_rows = []
    for t in tuples:
        inner = t[1:-1]
        vals = split_top_level_commas(inner)

        if len(vals) != len(cols):
            raise ValueError(
                f"Valores={len(vals)} != Colunas={len(cols)}. "
                "Tem valor complexo (vírgula/parênteses) fora do padrão."
            )

        new_rows.append("(" + ", ".join(vals[i] for i in keep_idx) + ")")

    out = (
        f"INSERT INTO {table} ({', '.join(new_cols)})\n"
        "VALUES  " + ",\n        ".join(new_rows)
    )
    if had_semicolon:
        out += ";"
    return out


def run():
    cols_remove = input("Colunas pra remover (separe por vírgula): ").strip()

    sql = read_insert_multiline()
    if not sql.strip():
        print("\n❌ Você não colou nada.\n")
        return

    out = process(sql, cols_remove)
    set_clipboard(out)

    print("\n✅ Pronto. Resultado COPIADO pro clipboard (Ctrl+V).\n")
    print(out)


