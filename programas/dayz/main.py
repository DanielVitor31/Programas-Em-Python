import os
import sys
import importlib.util

tipo = "Ferramentas DayZ"
descricao = "Scripts de suporte ao DayZ"

def get_current_module_dir():
    """
    Retorna SEMPRE o caminho real da pasta deste módulo.
    Funciona no Python normal e dentro do .exe com PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Estamos dentro do .exe — arquivos estão em _MEIPASS
        base = sys._MEIPASS  # type: ignore
        # dentro do _MEIPASS existe a pasta real "programas/dayz"
        return os.path.join(base, "programas", "dayz")
    else:
        # Rodando normal — usa o path real do arquivo
        return os.path.dirname(os.path.abspath(__file__))


def carregar_programas_locais():
    programas = []

    pasta = get_current_module_dir()  # <-- AQUI ESTAVA O TEU BUG

    for arquivo in sorted(os.listdir(pasta)):
        if not arquivo.endswith(".py"):
            continue

        nome = arquivo[:-3]

        if nome in ("main", "__init__"):
            continue

        caminho_modulo = os.path.join(pasta, arquivo)
        module_name = f"dayz_{nome}"

        spec = importlib.util.spec_from_file_location(module_name, caminho_modulo)
        if spec is None:
            print(f"Erro ao montar spec para {arquivo}")
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Erro ao importar {arquivo}: {e}")
            continue

        tipo_mod = getattr(module, "tipo", None)
        descricao_mod = getattr(module, "descricao", "")
        run_func = getattr(module, "run", None)

        if tipo_mod is None or not callable(run_func):
            print(f"Ignorando '{arquivo}': falta 'tipo' ou 'run()'.")
            continue

        programas.append({
            "tipo": tipo_mod,
            "descricao": descricao_mod,
            "run": run_func,
        })

    return programas


def mostrar_menu(programas):
    print("\n====== MENU DAYZ ======")
    print("0 - Voltar")
    for i, prog in enumerate(programas, start=1):
        linha = f"{i} - {prog['tipo']}"
        if prog["descricao"]:
            linha += f" - {prog['descricao']}"
        print(linha)
    print("========================\n")


def run():
    programas = carregar_programas_locais()

    if not programas:
        print("Nenhum programa encontrado em 'programas/dayz'.")
        return

    while True:
        mostrar_menu(programas)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Voltando ao menu principal...")
            break

        if opcao.isdigit() and 1 <= int(opcao) <= len(programas):
            prog = programas[int(opcao) - 1]
            print(f"\n=== Executando: {prog['tipo']} ===\n")
            try:
                prog["run"]()
            except Exception as e:
                print(f"Erro ao executar '{prog['tipo']}': {e}")
            print("\n=== Fim da execução (DayZ) ===\n")
        else:
            print("Opção inválida.\n")
