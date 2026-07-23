"""Classe base das cenas, com suporte a transicao em fade e warp entre cenas."""

from __future__ import annotations

from typing import Callable

import pygame

from ..transition import Fade


class Scene:
    def __init__(self, game) -> None:
        self.game = game
        self.fade: Fade | None = Fade("in")   # toda cena nasce clareando do preto
        self._warp: Callable[[], "Scene"] | None = None

    # -- transicao ---------------------------------------------------------
    def warp_to(self, factory: Callable[[], "Scene"]) -> None:
        """Inicia o fade de saida; ao terminar, troca para a cena criada."""
        if self.fade is None:
            self.fade = Fade("out")
            self._warp = factory

    def update_fade(self, dt: float) -> bool:
        """Atualiza o fade. Retorna True se a cena deve ficar 'congelada'."""
        if self.fade is None:
            return False
        if self.fade.update(dt):
            kind = self.fade.kind
            self.fade = None
            if kind == "out" and self._warp is not None:
                self.game.change_scene(self._warp())
        return True

    def draw_fade(self, surface: pygame.Surface) -> None:
        if self.fade is not None:
            self.fade.draw(surface)

    # -- interface ---------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:  # noqa: D401
        ...

    def update(self, dt: float) -> None:
        ...

    def draw(self, surface: pygame.Surface) -> None:
        ...
