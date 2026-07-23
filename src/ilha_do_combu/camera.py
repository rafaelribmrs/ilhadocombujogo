"""Camera que segue o jogador, presa aos limites do mapa."""

from __future__ import annotations

import pygame

from . import settings as cfg


class Camera:
    def __init__(self, map_w: int, map_h: int) -> None:
        self.map_w = map_w
        self.map_h = map_h
        self.x = 0
        self.y = 0

    def update(self, target: pygame.Rect) -> None:
        self.x = target.centerx - cfg.NATIVE_WIDTH // 2
        self.y = target.centery - cfg.NATIVE_HEIGHT // 2
        self.x = self._clamp(self.x, self.map_w, cfg.NATIVE_WIDTH)
        self.y = self._clamp(self.y, self.map_h, cfg.NATIVE_HEIGHT)

    @staticmethod
    def _clamp(value: int, map_size: int, view_size: int) -> int:
        if map_size <= view_size:
            # Mapa menor que a tela: centraliza (offset negativo).
            return (map_size - view_size) // 2
        return max(0, min(value, map_size - view_size))
