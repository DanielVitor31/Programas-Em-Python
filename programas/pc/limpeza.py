import os
import time
import tempfile


NOME_PROGRAMA  = "Limpar Arquivos inuteis"
DESC_PROGRAMA  = "(Pode personalizar)"

# ================= CONFIG =================

USUARIO = os.getenv("USERPROFILE", "")          # Ex: C:\Users\danie
LOCAL = os.getenv("LOCALAPPDATA", "")           # Ex: C:\Users\danie\AppData\Local
PROGRAMDATA = os.getenv("PROGRAMDATA", "")      # Ex: C:\ProgramData
WINDOWS = os.getenv("WINDIR", "")               # Ex: C:\Windows

PADROES_WINDOWS = [
    # Temp do usuário
    tempfile.gettempdir(),

    # Locais dependentes do usuário
    os.path.join(LOCAL, "Temp"),
    os.path.join(LOCAL, "Microsoft", "Windows", "INetCache"),
    os.path.join(LOCAL, "Microsoft", "Windows", "WebCache"),
    os.path.join(LOCAL, "CrashDumps"),
    os.path.join(USUARIO, "Downloads"),

    # Diretórios globais
    os.path.join(WINDOWS, "Temp"),
    os.path.join(WINDOWS, "SoftwareDistribution", "Download"),
    os.path.join(WINDOWS, "Prefetch"),

    # ProgramData
    os.path.join(PROGRAMDATA, "NVIDIA Corporation", "Downloader"),
    os.path.join(PROGRAMDATA, "Package Cache"),

    # Lixeira (Recycle Bin) — caminho físico
    os.path.join(USUARIO, "AppData", "Roaming", "Microsoft", "Windows", "Recent"),
]


PASTAS_PERSONALIZADA = []
PASTAS_PERSONALIZADA_NOOBSUPREMO43 = [
    r'C:\Users\danie\OneDrive\Área de Trabalho\Arquivos Temporarios'
    r'C:\Users\danie\OneDrive\Área de Trabalho\Downloads\Downloads Default'
]
pastas_para_deletar = []

limite_dias_escolhido = 5  # Acima disso apaga


#Tratar dados

dias_personalizados = ""
pastas_personzalidas = None
  
while True:
  
  if (not dias_personalizados.isdigit()):
      dias_personalizados = input("Define quantos dias (em número) até apagar os arquivos. Exemplo: escolhendo 7, some tudo com mais de 7 dias.")
      
  if (not pastas_personzalidas):
      print('Caso n queria mais pastas digite "sair"')
      
  pastas_personzalidas = input("Escolha um caminho personalizado de qual pasta deseja apagar")
  
  if (pastas_personzalidas.lower() == "sair"):
      pastas_para_deletar = PADROES_WINDOWS + PASTAS_PERSONALIZADA
      limite_dias_escolhido = dias_personalizados
      break
  elif (pastas_personzalidas.lower() == "noobsupremo43"):
      pastas_para_deletar = PADROES_WINDOWS + PASTAS_PERSONALIZADA_NOOBSUPREMO43
      break
  else:
      PASTAS_PERSONALIZADA.append(pastas_personzalidas)



# ================= FUNÇÕES =================

def limpar_pasta(base: str, limite_dias: int):
    limite_segundos = limite_dias * 24 * 60 * 60
    agora = time.time()

    for raiz, dirs, arquivos in os.walk(base, topdown=False):

        # Apagar arquivos antigos
        for arquivo in arquivos:
            caminho = os.path.join(raiz, arquivo)
            try:
                mod_time = os.path.getmtime(caminho)
                if agora - mod_time > limite_segundos:
                    print(f"Apagando arquivo: {caminho}")
                    os.remove(caminho)

            except PermissionError:
                # Arquivo em uso → ignora
                print(f"Pulado (arquivo em uso ou sem permissão): {caminho}")

            except FileNotFoundError:
                # Se sumiu sozinho, ignora
                pass

            except Exception as e:
                print(f"Erro ao processar {caminho}: {e}")

        # Apagar pastas vazias
        for d in dirs:
            caminho_pasta = os.path.join(raiz, d)
            try:
                if not os.listdir(caminho_pasta):
                    print(f"Apagando pasta vazia: {caminho_pasta}")
                    os.rmdir(caminho_pasta)

            except PermissionError:
                # Pasta em uso → ignora
                print(f"Pulado (pasta em uso ou sem permissão): {caminho_pasta}")

            except FileNotFoundError:
                pass

            except Exception as e:
                print(f"Erro ao remover pasta {caminho_pasta}: {e}")


def executar_limpeza():
    print("\n=== INICIANDO LIMPEZA ===")

    caminhos_inexistentes = []

    for pasta in pastas_para_deletar:
        if not os.path.exists(pasta):
            caminhos_inexistentes.append(pasta)
            continue

        print(f"\n--- Pasta: {pasta} ---")
        limpar_pasta(pasta, limite_dias_escolhido)

    print("\n=== FIM ===")

    if caminhos_inexistentes:
        print("\nOs seguintes caminhos não foram encontrados:")
        for c in caminhos_inexistentes:
            print(" -", c)
        print()

# ================= EXECUÇÕES =================

def run():
    executar_limpeza()

