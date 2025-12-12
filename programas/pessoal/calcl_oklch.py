NOME_PROGRAMA = "Calcular oklch"
DESC_PROGRAMA = "Calcula a cor base para cor desejada"

import re
import numpy as np



def parse_oklch(oklch_str, fallback):
    if not oklch_str.strip():
        return np.array(fallback), False

    match = re.match(
        r"oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*/\s*([\d.]+%?))?\s*\)",
        oklch_str.strip().lower()
    )
    if not match:
        raise ValueError("Formato inválido. Use: oklch(L C H) ou oklch(L C H / A)")

    l = float(match.group(1))
    c = float(match.group(2))
    h = float(match.group(3))

    a_raw = match.group(4)
    if a_raw:
        if a_raw.endswith("%"):
            a = float(a_raw[:-1]) / 100.0
        else:
            a = float(a_raw)
    else:
        a = 1.0

    return np.array([l, c, h, a]), bool(a_raw)


def calcular_operacoes(lch_base, lch_destino, include_alpha=False):
    ops = []
    labels = ['l', 'c', 'h'] + (['alpha'] if include_alpha else [])
    diffs = lch_destino - lch_base
    if not include_alpha:
        diffs = diffs[:3]

    for i, diff in enumerate(diffs):
        if include_alpha or abs(diff) > 0.001:
            sinal = "+" if diff > 0 else "-"
            valor = abs(round(diff, 4))
            if labels[i] == "h":
                ops.append(f'{labels[i]}: (base.h ?? 0) {sinal} {valor}')
            elif labels[i] == "alpha":
                ops.append(f'{labels[i]}: base.alpha {sinal} {valor}')
            else:
                ops.append(f'{labels[i]}: base.{labels[i]} {sinal} {valor}')
    return ops

def run():

    # Exibir menu
    print("\nSelecione uma cor base:")
    
    cor_base_input = input("Digite o número da opção: ").strip()
    
    if (cor_base_input == "p") :
        cor_base_input = "oklch(0.87 0.11 75.08 / 1.00)"

    cor_desejada = input("Digite a cor desejada em OKLCH: ").strip()

    lch_base, _ = parse_oklch(cor_base_input, None)
    lch_destino, dest_alpha_passado = parse_oklch(cor_desejada, None)

    include_alpha = dest_alpha_passado

    base_const = (
        f'const base = oklch({{ '
        f'l: {lch_base[0]}, c: {lch_base[1]}, h: {lch_base[2]}, alpha: {lch_base[3]}, mode: "oklch" }});'
    )
    ops_inline = ", ".join(calcular_operacoes(lch_base, lch_destino, include_alpha=include_alpha))

    if include_alpha:
        calc_array = [float(round(diff, 4)) for diff in (lch_destino - lch_base)]
    else:
        calc_array = [float(round(diff, 4)) for diff in (lch_destino[:3] - lch_base[:3])]

    print("\nConst gerado:")
    print(base_const)

    print("\nCalculos gerados:")
    print(calc_array)

    print("\nStyle gerado:")
    style_inline = f"culoriCalc({{ keyColorData: settingsColorsBaseData['pessoal'].value, calc: {calc_array} }})"
    print(style_inline)



