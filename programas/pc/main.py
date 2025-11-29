import os
import importlib

# Identificação desse módulo para o menu principal
tipo = "Ferramentas de PC"
descricao = "Scripts de limpeza, testes, etc."


def carregar_programas_locais():
    """
    Lê todos os .py dentro da pasta 'pc' (mesma pasta deste arquivo),
    exceto main.py e __init__.py, e tenta importar como:

        programas.pc.<nome_modulo>

    Cada módulo precisa ter:
        - tipo
        - descricao (opcional)
        - run()
    """
    programas = []

    # Caminho da pasta onde ESTE arquivo está
    dir_atual = os.path.dirname(os.path.abspath(__file__))

    for nome_arquivo in sorted(os.listdir(dir_atual)):
        if not nome_arquivo.endswith(".py"):
            continue

        base = os.path.splitext(nome_arquivo)[0]

        # pular o próprio main e o __init__
        if base in ("main", "__init__"):
            continue

        # Ex: programas.pc.limpeza
        full_module_name = f"{__package__}.{base}"  # __package__ = "programas.pc"

        try:
            module = importlib.import_module(full_module_name)
        except Exception as e:
            print(f"Erro ao importar módulo local {full_module_name}: {e}")
            continue

        tipo_mod = getattr(module, "tipo", None)
        descricao_mod = getattr(module, "descricao", "")
        run_func = getattr(module, "run", None)

        if tipo_mod is None or not callable(run_func):
            print(f"Ignorando {full_module_name}: falta 'tipo' ou função 'run()'.")
            continue

        programas.append({
            "tipo": str(tipo_mod),
            "descricao": str(descricao_mod),
            "run": run_func,
        })

    return programas


def mostrar_menu_local(programas):
    print("\n====== MENU PC ======")
    print("0 - Voltar")
    for idx, prog in enumerate(programas, start=1):
        linha = f"{idx} - {prog['tipo']}"
        if prog["descricao"]:
            linha += f" - {prog['descricao']}"
        print(linha)
    print("======================\n")


def run():
    """
    Função chamada pelo main principal.
    Aqui roda o menu interno de 'pc'.
    """
    programas = carregar_programas_locais()

    if not programas:
        print("Nenhum programa encontrado em 'programas/pc'.")
        return

    while True:
        mostrar_menu_local(programas)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Voltando ao menu principal...")
            break

        if not opcao.isdigit():
            print("Opção inválida.\n")
            continue

        idx = int(opcao)

        if 1 <= idx <= len(programas):
            prog = programas[idx - 1]
            print(f"\n=== Executando: {prog['tipo']} ===\n")
            try:
                prog["run"]()
            except Exception as e:
                print(f"Erro ao executar '{prog['tipo']}': {e}")
            print("\n=== Fim da execução (PC) ===\n")
        else:
            print("Opção inválida.\n")
