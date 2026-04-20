# =============================================================================
# TAIGA OS — main.py
# Ponto de entrada da aplicação.
#
# Como executar:
#   python main.py
#
# Dependências necessárias:
#   pip install customtkinter
#
# O banco de dados (taiga_os.db) é criado automaticamente na
# primeira execução, na mesma pasta deste arquivo.
# =============================================================================

import sys
import os

# Garante que o diretório raiz do projeto está no sys.path,
# para que os imports como `from controllers.xxx import ...` funcionem
# independente de onde o script é chamado.
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Verifica se o CustomTkinter está instalado antes de tentar iniciar.
try:
    import customtkinter  # noqa: F401
except ImportError:
    print(
        "\n[ERRO] CustomTkinter não encontrado.\n"
        "Instale com: pip install customtkinter\n"
    )
    sys.exit(1)

from views.main_window import TaigaApp


def main():
    """Inicializa e executa o loop principal da aplicação."""
    app = TaigaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
