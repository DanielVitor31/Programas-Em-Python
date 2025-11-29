import os
import sys
import importlib.util
import submenu_launcher


def get_base_dir():
    # Quando tiver congelado em .exe (PyInstaller)
    if getattr(sys, "frozen", False):
        # Se você usar --add-data, os arquivos vão pra pasta temporária _MEIPASS
        return sys._MEIPASS  # type: ignore
    # Quando rodar com Python normal
    return os.path.dirname(os.path.abspath(__file__))


def carregar_modulos_principais():
    base_dir = get_base_dir()
    programas_dir = os.path.join(base_dir, "programas")

    programas = []

    if not os.path.isdir(programas_dir):
        print(f"Pasta 'programas' não encontrada: {programas_dir}")
        return programas

    for nome_pasta in sorted(os.listdir(programas_dir)):
        caminho_pasta = os.path.join(programas_dir, nome_pasta)
        if not os.path.isdir(caminho_pasta):
            continue

        caminho_main = os.path.join(caminho_pasta, "main.py")
        if not os.path.isfile(caminho_main):
            continue

        # nome qualquer pro módulo
        mod_name = f"prog_{nome_pasta}"

        spec = importlib.util.spec_from_file_location(mod_name, caminho_main)
        if spec is None or spec.loader is None:
            print(f"Não foi possível carregar: {caminho_main}")
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Erro ao executar módulo {caminho_main}: {e}")
            continue

        tipo = getattr(module, "NOME_PROGRAMA", None)
        descricao = getattr(module, "DESC_PROGRAMA", "")
        run_func = getattr(module, "run", None)

        if tipo is None or not callable(run_func):
            print(f"Ignorando {caminho_main}: falta 'tipo' ou função 'run()'.")
            continue

        programas.append({
            "tipo": str(tipo),
            "descricao": str(descricao),
            "run": run_func,
        })

    return programas


def mostrar_menu_principal(programas):
    print("\n========== MENU PRINCIPAL ==========")
    print("0 - Sair")
    for idx, prog in enumerate(programas, start=1):
        linha = f"{idx} - {prog['tipo']}"
        if prog["descricao"]:
            linha += f" - {prog['descricao']}"
        print(linha)
    print("====================================\n")


def main():
    programas = carregar_modulos_principais()

    if not programas:
        print("Nenhum módulo encontrado em 'programas'.")
        input("Pressione ENTER para sair...")
        return

    while True:
        mostrar_menu_principal(programas)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Saindo...")
            break

        if not opcao.isdigit():
            print("Opção inválida.\n")
            continue

        idx = int(opcao)

        if 1 <= idx <= len(programas):
            prog = programas[idx - 1]
            print(f"\n=== Entrando em: {prog['tipo']} ===\n")
            try:
                prog["run"]()
            except Exception as e:
                print(f"Erro ao executar '{prog['tipo']}': {e}")
            print("\n=== Voltando ao menu principal ===\n")
        else:
            print("Opção inválida.\n")


if __name__ == "__main__":
    main()
