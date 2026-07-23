"""Carregamento da fonte do jogo (Jersey 10 -- fonte pixel, legivel e nitida)."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

import pygame


def get_asset_path(relative_path: str) -> str:
    """Retorna o caminho absoluto do recurso, funcionando no terminal e no PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        # No .exe compilado, o PyInstaller extrai tudo para a pasta temporária sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    
    # Em desenvolvimento, localiza a partir da raiz da pasta do pacote
    base_path = Path(__file__).parent.parent / "ilha_do_combu"
    return str(base_path / relative_path)


@lru_cache(maxsize=None)
def game_font(size: int) -> pygame.font.Font:
    """Carrega a fonte principal de forma segura e adaptável."""
    # Caminho exato mapeado no add-data do instalador
    font_path = get_asset_path(os.path.join("assets", "fonts", "Jersey10-Regular.ttf"))
    
    try:
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
    except Exception:
        pass

    # Sistema de segurança para não fechar o motor se o arquivo sumir
    return pygame.font.SysFont("Courier", size)