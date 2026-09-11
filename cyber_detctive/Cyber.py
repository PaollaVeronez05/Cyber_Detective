"""Ponto de entrada compatível com o nome antigo do projeto.

O jogo principal fica em ``cyber_detective.py``. Manter este arquivo como
atalho evita que o VS Code execute acidentalmente uma versão antiga.
"""

import flet as ft

from cyber_detective import main


if __name__ == "__main__":
    ft.run(main)
