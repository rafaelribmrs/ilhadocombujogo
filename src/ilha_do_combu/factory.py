"""Linha de producao de chocolate (fabrica da Dona Nena).

O cacau passa por estacoes diferentes e o personagem CARREGA o produto entre
elas:

  Bancada de preparo  -> quebra, fermentacao, secagem  => "sementes secas"
  Torra               -> "torrado"
  Moagem              -> "massa"
  Moldagem            -> +1 chocolate no cesto
  Banca               -> vende quando o cesto enche (3 chocolates)

A ``PrepBench`` tem estado interno (as 3 primeiras etapas). As demais estacoes
(``Station``) sao so lugares; a transformacao depende do que o jogador carrega,
e e resolvida pela cena.
"""

from __future__ import annotations

import pygame

EMPTY, BEANS, FERMENTED, DRIED = range(4)

_BUSY = ("Mãos ocupadas", [
    "Você já está carregando algo! Leve até a próxima estação antes de pegar "
    "mais.",
])
_NO_CACAU = ("Bancada de Preparo", [
    "A bancada está vazia. Colha cacau na horta primeiro!",
])
_PREP = {
    EMPTY: ("Quebra dos frutos", [
        "Você abriu os frutos e tirou as sementes, envoltas na polpa branca e "
        "doce.",
    ]),
    BEANS: ("Fermentação", [
        "As sementes fermentam enroladas em folha de bananeira. É aqui que nasce "
        "o sabor do chocolate!",
    ]),
    FERMENTED: ("Secagem", [
        "As sementes secaram ao sol. Agora pegue-as e leve para a TORRA!",
    ]),
}
_PICKUP = ("Sementes secas", [
    "Você pegou as sementes secas no cesto. Leve-as até a estação de TORRA.",
])


class PrepBench:
    def __init__(self, x: int, y: int, bench: pygame.Surface, items: list) -> None:
        self.x = x
        self.y = y
        self.bench = bench
        self.items = items     # [None, beans, fermented, dried, ...]
        self.stage = EMPTY
        w, h = bench.get_size()
        self.interact = pygame.Rect(x - 6, y - 10, w + 12, h + 20)
        self.solid = pygame.Rect(x + 2, y + h - 7, w - 4, 6)

    @property
    def sort_y(self) -> int:
        return self.y + self.bench.get_height()

    def act(self, scene) -> tuple[str, list[str]]:
        if scene.carrying is not None:
            return _BUSY
        if self.stage == EMPTY:
            if scene.harvested <= 0:
                return _NO_CACAU
            scene.harvested -= 1
            self.stage = BEANS
            return _PREP[EMPTY]
        if self.stage in (BEANS, FERMENTED):
            text = _PREP[self.stage]
            self.stage += 1
            return text
        # DRIED -> o jogador pega as sementes secas
        scene.carrying = "dried"
        self.stage = EMPTY
        return _PICKUP

    def draw(self, target: pygame.Surface, camera) -> None:
        target.blit(self.bench, (self.x - camera.x, self.y - camera.y))
        item = self.items[self.stage]
        if item is not None:
            iw, ih = item.get_size()
            target.blit(item, (self.x + 9 - iw // 2 - camera.x,
                               self.y + 8 - ih - camera.y))


class Station:
    """Lugar fixo (torra, moagem, moldagem, banca). So desenha e detecta foco."""

    def __init__(self, name: str, label: str, x: int, y: int,
                 surf: pygame.Surface) -> None:
        self.name = name
        self.label = label
        self.x = x
        self.y = y
        self.surf = surf
        w, h = surf.get_size()
        self.solid = pygame.Rect(x + 2, y + h - 7, w - 4, 6)
        self.interact = pygame.Rect(x - 6, y - 10, w + 12, h + 20)

    @property
    def sort_y(self) -> int:
        return self.y + self.surf.get_height()

    def draw(self, target: pygame.Surface, camera) -> None:
        target.blit(self.surf, (self.x - camera.x, self.y - camera.y))
