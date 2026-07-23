"""Caixa de dialogo estilo Pokemon Emerald.

Caixa clara com borda azul-marinho dupla e cantos arredondados, texto escuro
(fonte pixel Jersey 10), efeito maquina-de-escrever, nome do falante numa abinha
e seta piscando. Textos longos sao paginados automaticamente em blocos de ate
``MAX_LINES`` linhas, para nunca estourar a caixa.
"""

from __future__ import annotations

import pygame

from . import settings as cfg

TYPE_SPEED = 42.0  # caracteres por segundo
MAX_LINES = 3      # linhas por pagina
PAD = 7


class DialogueBox:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.line_h = font.get_height()
        # A caixa e dimensionada a partir da fonte (cabe MAX_LINES linhas).
        box_h = MAX_LINES * self.line_h + 2 * PAD + 4
        self.box = pygame.Rect(5, cfg.NATIVE_HEIGHT - box_h - 4,
                               cfg.NATIVE_WIDTH - 10, box_h)
        self.active = False
        self.speaker = ""
        self._pages: list[list[str]] = []
        self._page = 0
        self._shown = 0.0
        self._blink = 0.0

    # -- controle ----------------------------------------------------------
    def open(self, text: str | list[str], speaker: str = "") -> None:
        chunks = [text] if isinstance(text, str) else list(text)
        max_w = self.box.width - 2 * PAD
        self._pages = []
        for chunk in chunks:
            lines = self._wrap(chunk, max_w)
            for i in range(0, len(lines), MAX_LINES):
                self._pages.append(lines[i:i + MAX_LINES])
        self._page = 0
        self._shown = 0.0
        self.speaker = speaker
        self.active = True

    def advance(self) -> None:
        if not self.active:
            return
        full = self._page_len(self._page)
        if self._shown < full:
            self._shown = full
            return
        self._page += 1
        if self._page >= len(self._pages):
            self.active = False
        else:
            self._shown = 0.0

    # -- ciclo -------------------------------------------------------------
    def update(self, dt: float) -> None:
        if not self.active:
            return
        self._blink = (self._blink + dt) % 1.0
        full = self._page_len(self._page)
        if self._shown < full:
            self._shown = min(full, self._shown + TYPE_SPEED * dt)

    def draw(self, target: pygame.Surface) -> None:
        if not self.active:
            return
        self._draw_frame(target, self.box)
        if self.speaker:
            self._draw_name_tab(target)

        shown = int(self._shown)
        used = 0
        y = self.box.y + PAD
        for line in self._pages[self._page]:
            take = max(0, min(len(line), shown - used))
            if take > 0:
                self._draw_text(target, line[:take], self.box.x + PAD, y)
            used += len(line)
            y += self.line_h

        if self._shown >= self._page_len(self._page) and self._blink < 0.5:
            ax = self.box.right - PAD - 4
            ay = self.box.bottom - PAD - 1
            pygame.draw.polygon(target, cfg.DLG_BORDER,
                                [(ax, ay), (ax + 6, ay), (ax + 3, ay + 4)])

    # -- desenho -----------------------------------------------------------
    @staticmethod
    def _draw_frame(target: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(target, cfg.DLG_BORDER, rect, border_radius=6)
        pygame.draw.rect(target, cfg.DLG_BORDER2, rect.inflate(-4, -4), border_radius=5)
        pygame.draw.rect(target, cfg.DLG_BG, rect.inflate(-6, -6), border_radius=4)

    def _draw_name_tab(self, target: pygame.Surface) -> None:
        label = self.font.render(self.speaker, True, cfg.DLG_TEXT)
        w = label.get_width() + 12
        tab = pygame.Rect(self.box.x + 8, self.box.y - self.line_h - 1,
                          w, self.line_h + 3)
        self._draw_frame(target, tab)
        target.blit(label, (tab.x + 6, tab.y + 2))

    def _draw_text(self, target: pygame.Surface, text: str, x: int, y: int) -> None:
        shadow = self.font.render(text, True, cfg.DLG_SHADOW)
        main = self.font.render(text, True, cfg.DLG_TEXT)
        target.blit(shadow, (x + 1, y + 1))
        target.blit(main, (x, y))

    # -- helpers -----------------------------------------------------------
    def _page_len(self, page: int) -> int:
        return sum(len(line) for line in self._pages[page])

    def _wrap(self, text: str, max_w: int) -> list[str]:
        lines: list[str] = []
        cur = ""
        for word in text.split():
            test = f"{cur} {word}".strip()
            if self.font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines or [""]
