import os
import sys
import importlib.util


def _get_base_dir():
    # Onde estão os arquivos quando vira .exe (PyInstaller)
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore
    # Rodando normal com Python
    return os.path.dirname(os.path.abspath(__file__))


def run_submenu(folder_name: str, titulo_menu: str):
    """
    folder_name: nome da subpasta dentro de 'programas' (ex: 'pc', 'dayz')
    titulo_menu: texto do título do menu (ex: 'MENU PC', 'MENU DAYZ')
    """
    base_dir = _get_base_dir()
    pasta = os.path.join(base_dir, "programas", folder_name)

    if not os.path.isdir(pasta):
        print(f"Pasta de módulos não encontrada: {pasta}")
        return

    programas = []

    # Carrega todos os .py da pasta (menos main/__init__)
    for arquivo in sorted(os.listdir(pasta)):
        if not arquivo.endswith(".py"):
            continue

        nome = arquivo[:-3]
        if nome in ("main", "__init__"):
            continue

        caminho_modulo = os.path.join(pasta, arquivo)
        module_name = f"{folder_name}_{nome}"

        spec = importlib.util.spec_from_file_location(module_name, caminho_modulo)
        if spec is None or spec.loader is None:
            print(f"[{folder_name}] Erro ao montar spec para {arquivo}")
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"[{folder_name}] Erro ao importar {arquivo}: {e}")
            continue

        tipo_mod = getattr(module, "tipo", None)
        descricao_mod = getattr(module, "descricao", "")
        run_func = getattr(module, "run", None)

        if tipo_mod is None or not callable(run_func):
            print(f"[{folder_name}] Ignorando '{arquivo}': falta 'tipo' ou 'run()'.")
            continue

        programas.append({
            "tipo": str(tipo_mod),
            "descricao": str(descricao_mod),
            "run": run_func,
        })

    if not programas:
        print(f"Nenhum programa encontrado em 'programas/{folder_name}'.")
        return

    # Loop do menu
    while True:
        print(f"\n====== {titulo_menu} ======")
        print("0 - Voltar")
        for i, prog in enumerate(programas, start=1):
            linha = f"{i} - {prog['tipo']}"
            if prog["descricao"]:
                linha += f" - {prog['descricao']}"
            print(linha)
        print("=" * (10 + len(titulo_menu)) + "\n")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Voltando...")
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
            print(f"\n=== Fim da execução ({titulo_menu}) ===\n")
        else:
            print("Opção inválida.\n")
