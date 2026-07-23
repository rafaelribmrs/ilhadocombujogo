"""Transicao em fade (escurece/clareia a tela), como nos warps de Pokemon."""

from __future__ import annotations

import pygame

from . import settings as cfg

FADE_DURATION = 0.35  # segundos


class Fade:
    def __init__(self, kind: str = "in", duration: float = FADE_DURATION) -> None:
        self.kind = kind            # "in" (do preto p/ cena) ou "out" (cena p/ preto)
        self.duration = duration
        self.t = 0.0
        self._overlay = pygame.Surface((cfg.NATIVE_WIDTH, cfg.NATIVE_HEIGHT))
        self._overlay.fill(cfg.BLACK)

    def update(self, dt: float) -> bool:
        """Avanca o fade. Retorna True quando termina."""
        self.t = min(self.duration, self.t + dt)
        return self.t >= self.duration

    def draw(self, target: pygame.Surface) -> None:
        progress = self.t / self.duration if self.duration else 1.0
        alpha = 1.0 - progress if self.kind == "in" else progress
        self._overlay.set_alpha(int(255 * alpha))
        target.blit(self._overlay, (0, 0))
