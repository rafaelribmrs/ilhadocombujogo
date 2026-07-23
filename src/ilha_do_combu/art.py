"""Geracao procedural de toda a arte em pixel art.

Nada de imagens externas: cada sprite e desenhado em codigo, na resolucao
nativa (tiles 16x16), com uma paleta coesa de tons amazonicos. Isso mantem o
projeto leve e garante um estilo unificado. Sprites de IA podem substituir
estes assets depois, mas o jogo ja roda bonito so com isto.

Duas tecnicas sao usadas:
  * ``from_grid`` -> sprites desenhados pixel a pixel a partir de um "mapa"
    de caracteres (personagem, objetos pequenos);
  * funcoes ``tile_*`` / ``prop_*`` -> texturas desenhadas com primitivas
    (pisos, paredes, moveis maiores).
"""

from __future__ import annotations

import random

import pygame

from . import settings as cfg

T = cfg.TILE_SIZE

# Paleta indexada por caractere -------------------------------------------------
# '.' e ' ' = transparente.
PALETTE: dict[str, tuple[int, int, int]] = {
    "o": (26, 20, 16),      # contorno (quase preto)
    "s": (207, 155, 107),   # pele
    "d": (156, 107, 66),    # pele sombra
    "h": (42, 28, 18),      # cabelo
    "H": (74, 51, 32),      # cabelo brilho
    "t": (63, 163, 77),     # camisa (verde)
    "T": (44, 122, 55),     # camisa sombra
    "b": (58, 90, 156),     # bermuda (azul)
    "B": (40, 64, 110),     # bermuda sombra
    "c": (170, 96, 52),     # barro/ceramica
    "C": (132, 70, 38),     # barro sombra
    "g": (96, 170, 86),     # folha clara
    "G": (44, 110, 58),     # folha escura
    "y": (226, 184, 92),    # palha/amarelo
    "r": (176, 64, 56),     # vermelho (rede)
    "p": (104, 64, 132),    # roxo (acai)
    "P": (78, 46, 104),     # roxo escuro (acai sombra)
    "w": (140, 198, 214),   # ceu/agua clara
    "k": (245, 240, 230),   # branco
}


def from_grid(rows: list[str], palette: dict[str, tuple[int, int, int]] | None = None) -> pygame.Surface:
    """Cria uma Surface a partir de linhas de texto (1 caractere por pixel)."""
    pal = palette or PALETTE
    h = len(rows)
    w = max(len(r) for r in rows) if rows else 0
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in (".", " "):
                continue
            surf.set_at((x, y), pal.get(ch, (255, 0, 255)))
    return surf


# --- Personagem (crianca paraense, estilo Pokemon Emerald) --------------------
# Sprite alto 16x24 (cabeca grande, cabelo escuro), 4 direcoes e quadros de
# caminhada. LEFT e o espelho de RIGHT. Os pes ficam na base do sprite.

_HEAD_DOWN = [
    "................",
    "....oooooooo....",
    "...ohhhhhhhho...",
    "..ohhhhhhhhhho..",
    "..ohHHHHHHHHho..",
    "..ohhsssssshho..",
    "..ohssossossho..",
    "..ohssssssssho..",
    "...odssssssdo...",
    ".....dssssd.....",
]
_HEAD_UP = [
    "................",
    "....oooooooo....",
    "...ohhhhhhhho...",
    "..ohhhhhhhhhho..",
    "..ohHHHHHHHHho..",
    "..ohhhhhhhhhho..",
    "..ohhhhhhhhhho..",
    "..ohhhhhhhhhho..",
    "...ohhhhhhhho...",
    ".....dssssd.....",
]
_HEAD_RIGHT = [
    "................",
    "....oooooooo....",
    "...ohhhhhhhho...",
    "..ohhhhhhhsso...",
    "..ohhhhhhssso...",
    "..ohhhhhsosso...",
    "..ohhhhhssddo...",
    "..ohhhhsssddo...",
    "...ohhhsssddo...",
    ".....dsssd......",
]

# Tronco + bracos (comum as direcoes). Os bracos (pele) saem dos lados e
# terminam em maozinhas (pele sombra).
_BODY = [
    "...otttttttto...",
    "..osttttttttso..",
    "..osttttttttso..",
    "..odttttttttdo..",
    "...oTTTTTTTTo...",
    "...obbbbbbbbo...",
    "...obBBBBBBbo...",
    "...obbbbbbbbo...",
]

# Pernas: 3 variacoes para a caminhada (6 linhas cada).
_LEGS_IDLE = [
    "....obb..bbo....",
    ".....ss..ss.....",
    ".....ss..ss.....",
    ".....dd..dd.....",
    "....odd..ddo....",
    "................",
]
_LEGS_STEP_A = [
    "....obb..bbo....",
    ".....ss..ss.....",
    ".....ss..dd.....",
    ".....dd..d......",
    "....odd...o.....",
    "................",
]
_LEGS_STEP_B = [
    "....obb..bbo....",
    ".....ss..ss.....",
    ".....dd..ss.....",
    "......d..dd.....",
    ".....o...ddo....",
    "................",
]


def _build_char_frame(head: list[str], legs: list[str]) -> pygame.Surface:
    return from_grid(head + _BODY + legs)


def build_character() -> dict[str, list[pygame.Surface]]:
    """Retorna {direcao: [idle, stepA, idle, stepB]} para cada direcao."""
    frames: dict[str, list[pygame.Surface]] = {}
    for name, head in (("down", _HEAD_DOWN), ("up", _HEAD_UP), ("right", _HEAD_RIGHT)):
        idle = _build_char_frame(head, _LEGS_IDLE)
        step_a = _build_char_frame(head, _LEGS_STEP_A)
        step_b = _build_char_frame(head, _LEGS_STEP_B)
        frames[name] = [idle, step_a, idle, step_b]
    frames["left"] = [pygame.transform.flip(f, True, False) for f in frames["right"]]
    return frames


# --- Tiles do cenario ----------------------------------------------------------

def _noise(surf: pygame.Surface, color: tuple[int, int, int], n: int, rng: random.Random) -> None:
    w, h = surf.get_size()
    for _ in range(n):
        surf.set_at((rng.randrange(w), rng.randrange(h)), color)


# Tons das paredes (mais escuros que o piso, para dar contraste).
_WALL_BASE = (62, 43, 28)
_WALL_SEAM = (40, 27, 17)
_WALL_FACE = (86, 61, 39)
_WALL_CAP = (120, 88, 56)
_WALL_FOOT = (30, 20, 13)


def tile_floor() -> pygame.Surface:
    """Piso de tabuas horizontais -- claro e calmo, contrasta com as paredes."""
    s = pygame.Surface((T, T))
    rng = random.Random(7)
    s.fill(cfg.WOOD_LIGHT)
    # juntas horizontais suaves (tabuas de ~8px)
    for y in (0, 8):
        pygame.draw.line(s, cfg.WOOD, (0, y), (T - 1, y))
        pygame.draw.line(s, cfg.WOOD_HILIGHT, (0, y + 1), (T - 1, y + 1))
    # veios sutis da madeira
    for _ in range(4):
        x = rng.randrange(T)
        y = 2 + rng.randrange(5) + 8 * rng.randrange(2)
        pygame.draw.line(s, cfg.WOOD, (x, y), (min(T - 1, x + 3), y))
    return s


def tile_wall() -> pygame.Surface:
    """Parede de tabuas verticais, escura."""
    s = pygame.Surface((T, T))
    s.fill(_WALL_BASE)
    for x in range(0, T, 4):
        pygame.draw.line(s, _WALL_SEAM, (x, 0), (x, T - 1))       # junta escura
        pygame.draw.line(s, _WALL_FACE, (x + 1, 0), (x + 1, T - 1))  # face da tabua
    return s


def tile_wall_top() -> pygame.Surface:
    """Topo da parede: viga em cima e sombra embaixo (onde encontra o chao)."""
    s = tile_wall()
    pygame.draw.rect(s, _WALL_CAP, (0, 0, T, 4))            # viga
    pygame.draw.line(s, cfg.WOOD_HILIGHT, (0, 0), (T - 1, 0))
    pygame.draw.line(s, _WALL_SEAM, (0, 4), (T - 1, 4))
    pygame.draw.rect(s, _WALL_FOOT, (0, T - 3, T, 3))      # sombra na base
    return s


def tile_window() -> pygame.Surface:
    """Janela na parede de cima, com vista do rio e da mata."""
    s = tile_wall_top()
    pygame.draw.rect(s, _WALL_SEAM, (2, 3, 12, 10))        # vao
    pygame.draw.rect(s, cfg.SKY, (3, 4, 10, 4))            # ceu
    pygame.draw.rect(s, cfg.RIVER, (3, 8, 10, 4))          # rio
    pygame.draw.rect(s, cfg.LEAF_DARK, (3, 7, 4, 2))       # mata na margem
    pygame.draw.rect(s, cfg.LEAF, (9, 6, 3, 3))            # arvore
    # caixilho
    pygame.draw.rect(s, _WALL_FACE, (2, 3, 12, 10), 1)
    pygame.draw.line(s, _WALL_FACE, (8, 3), (8, 12))
    pygame.draw.line(s, _WALL_FACE, (2, 8), (13, 8))
    return s


def _prop_rug() -> pygame.Surface:
    """Tapete de fibra (objeto colocado sobre o piso), com borda e franjas."""
    w, h = 46, 30
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    base = (178, 92, 70)        # terracota
    stripe = (148, 66, 50)
    light = (212, 150, 108)
    border = cfg.UI_BORDER      # creme
    pygame.draw.rect(s, base, (3, 1, w - 6, h - 2), border_radius=3)
    # listras quentes
    for y in range(5, h - 4, 6):
        pygame.draw.rect(s, stripe, (5, y, w - 10, 2))
        pygame.draw.rect(s, light, (5, y + 2, w - 10, 1))
    # borda e franjas
    pygame.draw.rect(s, border, (3, 1, w - 6, h - 2), 1, border_radius=3)
    for x in range(5, w - 4, 3):
        s.set_at((x, 0), border)
        s.set_at((x, h - 1), border)
    return s


# --- Objetos (props) -----------------------------------------------------------
# Podem ocupar mais de um tile. Desenhados a partir de grids.

_PROP_HAMMOCK = [  # rede (32x12) -- movel tradicional
    "..............................",
    "o............................o",
    "o.rrrrrrrrrrrrrrrrrrrrrrrrrr..o",
    "o.ryyrryyrryyrryyrryyrryyrr..o",
    "o.rkkrrkkrrkkrrkkrrkkrrkkrr..o",
    "o..ryyrryyrryyrryyrryyrryy...o",
    "o...rrrrrrrrrrrrrrrrrrrrr....o",
    "o....rrrrrrrrrrrrrrrrrrr.....o",
    "o.......................o....o",
    "o............................o",
    "oo..........................oo",
    "..............................",
]

_PROP_TABLE = [  # mesa de madeira 16x16
    "................",
    "..oooooooooooo..",
    ".occcccccccccco.",
    ".oCCCCCCCCCCCCo.",
    ".occcccccccccco.",
    ".oCCCCCCCCCCCCo.",
    "..oooooooooooo..",
    "...o........o...",
    "...o........o...",
    "...o........o...",
    "...o........o...",
    "...C........C...",
    "...C........C...",
    "...o........o...",
    "................",
    "................",
]

_PROP_SEEDLING = [  # vaso com muda de cacau 16x16 (centro educativo)
    "................",
    ".......g........",
    "......gGg.......",
    ".....gGGGg......",
    "...g.gGgGg.g....",
    "..gGg.gGg.gGg...",
    "..GGGg.G.gGGG...",
    "....GggGggG.....",
    "......oCo.......",
    ".....occco......",
    ".....cCcCc......",
    ".....cccCc......",
    ".....cCccc......",
    "......ooo.......",
    "................",
    "................",
]

_PROP_STOVE = [  # fogao a lenha de barro 16x16
    "................",
    "...oooooooooo...",
    "..occcccccccco..",
    "..oc.oooooo.co..",
    "..oc.orrrro.co..",
    "..oc.oryyro.co..",
    "..oc.oooooo.co..",
    "..occcccccccco..",
    "..oCCCCCCCCCCo..",
    "..oc.cccccc.co..",
    "..oc.cccccc.co..",
    "..occcccccccco..",
    "..oCCCCCCCCCCo..",
    "..ooCCCCCCCCoo..",
    "...o........o...",
    "................",
]

_PROP_BASKET = [  # cesto de acai 16x14
    "................",
    "....pppppp......",
    "...pPpPpPpp.....",
    "...pppPppPp.....",
    "...pPppPppp.....",
    "..oyyyyyyyyo....",
    "..oy.y.y.y.yo...",
    "..oyy.y.y.yyo...",
    "..oy.y.y.y.yo...",
    "..oyy.y.y.yyo...",
    "..oyyyyyyyyyo...",
    "...oooooooo.....",
    "................",
    "................",
]

_PROP_DOOR = [  # porta de saida 16x16
    "..oooooooooooo..",
    ".oCCCCCCCCCCCCo.",
    ".oCccccccccccCo.",
    ".oCcoooooooocCo.",
    ".oCcoBBBBBBocCo.",
    ".oCcoBwwwwBocCo.",
    ".oCcoBwBBwBocCo.",
    ".oCcoBwBBwBocCo.",
    ".oCcoBwwwwBocCo.",
    ".oCcoBBBByBocCo.",
    ".oCcoBBBBBBocCo.",
    ".oCcoooooooocCo.",
    ".oCccccccccccCo.",
    ".oCCCCCCCCCCCCo.",
    "..oooooooooooo..",
    "................",
]


# --- Decoracao da casa (moveis e enfeites) ------------------------------------

def _wood_cabinet(w: int, h: int, doors: int = 2) -> pygame.Surface:
    """Caixa de madeira com portas, macanetas e pezinhos."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD, (1, 0, w - 2, h - 2))
    pygame.draw.rect(s, cfg.WOOD_LIGHT, (1, 0, w - 2, 2))
    pygame.draw.rect(s, cfg.WOOD_DARK, (1, 0, w - 2, h - 2), 1)
    dw = (w - 4) // doors
    for i in range(doors):
        dx = 2 + i * dw
        pygame.draw.rect(s, cfg.WOOD_DARK, (dx, 3, dw - 1, h - 7), 1)
        pygame.draw.line(s, cfg.WOOD_HILIGHT, (dx + 1, 4), (dx + 1, h - 6))
        kx = dx + dw - 3 if i == 0 else dx + 2
        pygame.draw.circle(s, cfg.WOOD_DARK, (kx, h // 2), 1)
    pygame.draw.rect(s, cfg.WOOD_DARK, (2, h - 2, 3, 2))
    pygame.draw.rect(s, cfg.WOOD_DARK, (w - 5, h - 2, 3, 2))
    return s


def _prop_tv() -> pygame.Surface:
    """TV de tubo simples (22x16)."""
    s = pygame.Surface((22, 16), pygame.SRCALPHA)
    body, body_d = (70, 68, 78), (46, 44, 54)
    screen, glow = (40, 52, 46), (130, 158, 138)
    pygame.draw.line(s, (50, 50, 50), (8, 0), (6, 5))
    pygame.draw.line(s, (50, 50, 50), (13, 0), (15, 5))
    pygame.draw.rect(s, body, (1, 4, 20, 11), border_radius=2)
    pygame.draw.rect(s, body_d, (1, 4, 20, 11), 1, border_radius=2)
    pygame.draw.rect(s, screen, (3, 6, 12, 7))
    pygame.draw.line(s, glow, (4, 7), (7, 7))
    pygame.draw.rect(s, body_d, (16, 6, 4, 7))
    s.set_at((18, 8), (190, 176, 96))
    s.set_at((18, 11), (120, 120, 130))
    pygame.draw.rect(s, body_d, (3, 15, 3, 1))
    pygame.draw.rect(s, body_d, (16, 15, 3, 1))
    return s


def _prop_cabinet() -> pygame.Surface:
    """Armario baixo / aparador (30x16), base para a TV."""
    return _wood_cabinet(30, 16, doors=3)


def _prop_nightstand() -> pygame.Surface:
    """Criado-mudo (14x14)."""
    return _wood_cabinet(14, 14, doors=1)


def _prop_wardrobe() -> pygame.Surface:
    """Guarda-roupa alto (22x30) com cornija no topo."""
    s = pygame.Surface((22, 30), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD_DARK, (0, 0, 22, 3))
    pygame.draw.rect(s, cfg.WOOD_LIGHT, (0, 1, 22, 1))
    s.blit(_wood_cabinet(22, 27, doors=2), (0, 3))
    return s


def _prop_counter() -> pygame.Surface:
    """Bancada de cozinha com pia (32x18)."""
    s = _wood_cabinet(32, 18, doors=3)
    pygame.draw.rect(s, cfg.WOOD_HILIGHT, (0, 0, 32, 3))
    pygame.draw.rect(s, cfg.WOOD_DARK, (0, 0, 32, 3), 1)
    pygame.draw.rect(s, (150, 156, 162), (20, 1, 9, 2))
    pygame.draw.rect(s, (96, 102, 110), (21, 1, 7, 1))
    pygame.draw.line(s, (120, 126, 132), (24, -1), (24, 1))
    return s


def _prop_sofa() -> pygame.Surface:
    """Sofa (32x18)."""
    s = pygame.Surface((32, 18), pygame.SRCALPHA)
    fab, fab_d, fab_l = (178, 96, 72), (146, 70, 52), (208, 140, 104)
    pygame.draw.rect(s, fab, (0, 3, 32, 13), border_radius=3)
    pygame.draw.rect(s, fab_d, (0, 3, 32, 13), 1, border_radius=3)
    pygame.draw.rect(s, fab, (0, 7, 4, 9))
    pygame.draw.rect(s, fab, (28, 7, 4, 9))
    pygame.draw.rect(s, fab_l, (5, 8, 10, 6), border_radius=2)
    pygame.draw.rect(s, fab_l, (17, 8, 10, 6), border_radius=2)
    pygame.draw.rect(s, cfg.WOOD_DARK, (2, 16, 3, 2))
    pygame.draw.rect(s, cfg.WOOD_DARK, (27, 16, 3, 2))
    return s


def _prop_sofa_up() -> pygame.Surface:
    """Sofa virado para cima (assento voltado para a TV, encosto perto da camera)."""
    s = pygame.Surface((32, 18), pygame.SRCALPHA)
    fab, fab_d, fab_l = (178, 96, 72), (146, 70, 52), (208, 140, 104)
    pygame.draw.rect(s, fab, (0, 2, 4, 14))            # bracos
    pygame.draw.rect(s, fab, (28, 2, 4, 14))
    pygame.draw.rect(s, fab_l, (5, 1, 10, 7), border_radius=2)   # assento (em cima)
    pygame.draw.rect(s, fab_l, (17, 1, 10, 7), border_radius=2)
    pygame.draw.rect(s, fab_d, (5, 1, 22, 7), 1, border_radius=2)
    pygame.draw.rect(s, fab, (2, 8, 28, 8), border_radius=2)     # encosto (embaixo)
    pygame.draw.rect(s, fab_d, (2, 8, 28, 8), 1, border_radius=2)
    pygame.draw.rect(s, fab_d, (0, 2, 4, 14), 1)
    pygame.draw.rect(s, fab_d, (28, 2, 4, 14), 1)
    pygame.draw.rect(s, cfg.WOOD_DARK, (3, 16, 3, 2))           # pes
    pygame.draw.rect(s, cfg.WOOD_DARK, (26, 16, 3, 2))
    return s


def _prop_shelf() -> pygame.Surface:
    """Prateleira de parede com livros e pote (22x14)."""
    s = pygame.Surface((22, 14), pygame.SRCALPHA)
    pygame.draw.rect(s, (176, 80, 70), (3, 2, 3, 7))
    pygame.draw.rect(s, (90, 150, 90), (7, 1, 3, 8))
    pygame.draw.rect(s, (90, 120, 180), (11, 3, 3, 6))
    pygame.draw.ellipse(s, cfg.WOOD_HILIGHT, (15, 3, 5, 6))
    pygame.draw.rect(s, cfg.WOOD, (0, 9, 22, 3))
    pygame.draw.rect(s, cfg.WOOD_DARK, (0, 9, 22, 3), 1)
    pygame.draw.rect(s, cfg.WOOD_DARK, (2, 12, 2, 2))
    pygame.draw.rect(s, cfg.WOOD_DARK, (18, 12, 2, 2))
    return s


def _prop_potplant() -> pygame.Surface:
    """Planta decorativa em vaso (16x20)."""
    s = pygame.Surface((16, 20), pygame.SRCALPHA)
    for cx, cy, r, col in [(8, 7, 6, cfg.LEAF_DARK), (5, 6, 4, cfg.LEAF),
                           (11, 6, 4, cfg.LEAF), (8, 4, 4, cfg.LEAF_LIGHT)]:
        pygame.draw.circle(s, col, (cx, cy), r)
    pygame.draw.rect(s, (170, 96, 52), (4, 12, 8, 7))
    pygame.draw.rect(s, (132, 70, 38), (4, 12, 8, 2))
    pygame.draw.rect(s, (26, 20, 16), (4, 12, 8, 7), 1)
    return s


def _prop_waterjar() -> pygame.Surface:
    """Talha / pote de barro de agua (16x18)."""
    s = pygame.Surface((16, 18), pygame.SRCALPHA)
    c, cd, cl = (170, 96, 52), (132, 70, 38), (200, 130, 80)
    pygame.draw.ellipse(s, c, (2, 4, 12, 13))
    pygame.draw.ellipse(s, cd, (2, 4, 12, 13), 1)
    pygame.draw.ellipse(s, cl, (4, 6, 4, 5))
    pygame.draw.rect(s, cd, (5, 2, 6, 3))
    pygame.draw.rect(s, c, (5, 1, 6, 2))
    pygame.draw.rect(s, cd, (3, 16, 10, 2))
    return s


def _prop_picture() -> pygame.Surface:
    """Quadro de parede com paisagem (14x12)."""
    s = pygame.Surface((14, 12), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD_DARK, (0, 0, 14, 12))
    pygame.draw.rect(s, cfg.WOOD_HILIGHT, (0, 0, 14, 12), 1)
    pygame.draw.rect(s, cfg.SKY, (2, 2, 10, 4))
    pygame.draw.rect(s, cfg.RIVER, (2, 6, 10, 4))
    pygame.draw.rect(s, cfg.LEAF, (3, 4, 3, 3))
    pygame.draw.rect(s, cfg.LEAF_DARK, (8, 5, 3, 2))
    return s


def _prop_clock() -> pygame.Surface:
    """Relogio de parede (12x12)."""
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(s, cfg.WOOD_DARK, (6, 6), 6)
    pygame.draw.circle(s, (245, 240, 230), (6, 6), 5)
    pygame.draw.line(s, (26, 20, 16), (6, 6), (6, 3))
    pygame.draw.line(s, (26, 20, 16), (6, 6), (9, 6))
    s.set_at((6, 1), (26, 20, 16))
    s.set_at((6, 11), (26, 20, 16))
    return s


def build_props() -> dict[str, pygame.Surface]:
    return {
        "hammock": from_grid(_PROP_HAMMOCK),
        "table": from_grid(_PROP_TABLE),
        "seedling": from_grid(_PROP_SEEDLING),
        "stove": from_grid(_PROP_STOVE),
        "basket": from_grid(_PROP_BASKET),
        "door": from_grid(_PROP_DOOR),
        "rug": _prop_rug(),
        "tv": _prop_tv(),
        "cabinet": _prop_cabinet(),
        "nightstand": _prop_nightstand(),
        "wardrobe": _prop_wardrobe(),
        "counter": _prop_counter(),
        "sofa": _prop_sofa(),
        "sofa_up": _prop_sofa_up(),
        "shelf": _prop_shelf(),
        "potplant": _prop_potplant(),
        "waterjar": _prop_waterjar(),
        "picture": _prop_picture(),
        "clock": _prop_clock(),
    }


def build_tiles() -> dict[str, pygame.Surface]:
    return {
        "floor": tile_floor(),
        "wall": tile_wall(),
        "wall_top": tile_wall_top(),
        "window": tile_window(),
    }


# --- Overworld (estilo Pokemon Emerald) ---------------------------------------

def tile_grass() -> pygame.Surface:
    s = pygame.Surface((T, T))
    rng = random.Random(11)
    s.fill(cfg.GRASS)
    for _ in range(12):
        s.set_at((rng.randrange(T), rng.randrange(T)), cfg.GRASS_DARK)
    for _ in range(8):
        s.set_at((rng.randrange(T), rng.randrange(T)), cfg.GRASS_LIGHT)
    for _ in range(3):
        x, y = rng.randrange(2, 14), rng.randrange(5, 14)
        pygame.draw.line(s, cfg.GRASS_DARK, (x, y), (x, y - 2))
    return s


def tile_grass_tall() -> pygame.Surface:
    """Mato alto, marca registrada do overworld de Pokemon."""
    s = tile_grass()
    pygame.draw.rect(s, cfg.GRASS_DARK, (0, 8, T, 8))
    for x in range(1, T, 3):
        pygame.draw.line(s, cfg.GRASS, (x, 15), (x, 7))
        pygame.draw.line(s, cfg.GRASS_LIGHT, (x + 1, 15), (x + 1, 10))
    pygame.draw.line(s, cfg.GRASS_DARK, (0, 15), (T - 1, 15))
    return s


def tile_path() -> pygame.Surface:
    s = pygame.Surface((T, T))
    rng = random.Random(5)
    s.fill(cfg.PATH)
    for _ in range(14):
        s.set_at((rng.randrange(T), rng.randrange(T)), cfg.PATH_DARK)
    return s


def tile_water() -> pygame.Surface:
    s = pygame.Surface((T, T))
    s.fill(cfg.WATER)
    for y in (3, 11):
        pygame.draw.line(s, cfg.WATER_DARK, (0, y), (T - 1, y))
        pygame.draw.line(s, cfg.WATER_LIGHT, (2, y - 1), (7, y - 1))
    pygame.draw.line(s, cfg.WATER_LIGHT, (9, 6), (13, 6))
    return s


def tile_fence() -> pygame.Surface:
    """Cerca de madeira sobre a grama (solida)."""
    s = tile_grass()
    pygame.draw.rect(s, cfg.TRUNK, (2, 2, 2, 12))
    pygame.draw.rect(s, cfg.TRUNK, (12, 2, 2, 12))
    pygame.draw.rect(s, cfg.WOOD_LIGHT, (0, 4, T, 2))
    pygame.draw.rect(s, cfg.WOOD, (0, 9, T, 2))
    return s


def _prop_tree(pods: bool = False) -> pygame.Surface:
    s = pygame.Surface((32, 40), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.TRUNK, (13, 26, 6, 13))      # tronco
    pygame.draw.rect(s, (84, 56, 32), (13, 26, 2, 13))
    for cx, cy, r, col in [
        (16, 16, 14, cfg.LEAF_DARK),
        (10, 15, 8, cfg.LEAF),
        (21, 13, 8, cfg.LEAF),
        (16, 10, 8, cfg.LEAF_LIGHT),
        (13, 18, 5, cfg.LEAF_LIGHT),
    ]:
        pygame.draw.circle(s, col, (cx, cy), r)
    if pods:  # frutos de cacau no tronco
        for px, py in [(9, 28), (20, 27), (14, 33)]:
            pygame.draw.ellipse(s, cfg.FLOWER_Y, (px, py, 4, 7))
            pygame.draw.ellipse(s, (198, 132, 56), (px, py, 4, 7), 1)
    return s


def _prop_house_exterior() -> pygame.Surface:
    """Palafita vista de fora, com telhado de palha, janela, porta e estacas."""
    s = pygame.Surface((48, 52), pygame.SRCALPHA)
    for sx in (9, 24, 39):                               # estacas
        pygame.draw.rect(s, cfg.WOOD_DARK, (sx - 1, 40, 3, 12))
    pygame.draw.rect(s, cfg.WOOD, (4, 18, 40, 24))       # corpo
    pygame.draw.rect(s, cfg.WOOD_LIGHT, (4, 18, 40, 2))
    pygame.draw.rect(s, cfg.WOOD_DARK, (4, 18, 40, 24), 1)
    pygame.draw.polygon(s, cfg.WOOD_DARK, [(0, 19), (48, 19), (24, 2)])   # telhado
    pygame.draw.polygon(s, cfg.WALL_LIGHT, [(3, 18), (45, 18), (24, 4)])
    for i in range(6, 44, 4):
        pygame.draw.line(s, cfg.WOOD_DARK, (24, 5), (i, 18))
    pygame.draw.rect(s, cfg.RIVER_DARK, (9, 24, 9, 9))   # janela
    pygame.draw.rect(s, cfg.SKY, (10, 25, 7, 3))
    pygame.draw.rect(s, cfg.RIVER, (10, 28, 7, 4))
    pygame.draw.rect(s, cfg.WOOD_DARK, (9, 24, 9, 9), 1)
    pygame.draw.rect(s, cfg.WOOD_DARK, (28, 26, 11, 16))  # porta
    pygame.draw.rect(s, (62, 41, 25), (29, 27, 9, 15))
    pygame.draw.circle(s, cfg.WOOD_HILIGHT, (36, 34), 1)
    return s


def _prop_sign() -> pygame.Surface:
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD_DARK, (7, 8, 2, 7))
    pygame.draw.rect(s, cfg.WOOD, (2, 2, 12, 8))
    pygame.draw.rect(s, cfg.WOOD_DARK, (2, 2, 12, 8), 1)
    pygame.draw.line(s, cfg.WOOD_LIGHT, (4, 5), (11, 5))
    pygame.draw.line(s, cfg.WOOD_LIGHT, (4, 7), (9, 7))
    return s


def _prop_flowers() -> pygame.Surface:
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    for x, y, c in [(4, 9, cfg.FLOWER_R), (10, 6, cfg.FLOWER_Y), (9, 12, cfg.FLOWER_R)]:
        pygame.draw.line(s, cfg.GRASS_DARK, (x, y + 1), (x, y + 4))
        pygame.draw.circle(s, c, (x, y), 2)
        s.set_at((x, y), cfg.WHITE)
    return s


def build_outdoor_tiles() -> dict[str, pygame.Surface]:
    return {
        "grass": tile_grass(),
        "grass_tall": tile_grass_tall(),
        "path": tile_path(),
        "water": tile_water(),
        "fence": tile_fence(),
    }


def build_outdoor_props() -> dict[str, pygame.Surface]:
    return {
        "tree": _prop_tree(False),
        "cacao_tree": _prop_tree(True),
        "house_exterior": _prop_house_exterior(),
        "sign": _prop_sign(),
        "flowers": _prop_flowers(),
    }


# --- Estagios de crescimento do cacau (mini-game de plantio) -------------------
# Cada estagio e um sprite de 16px de largura e altura variavel, alinhado pela
# base (o solo fica embaixo; a planta cresce para cima).

def _draw_soil(s: pygame.Surface, tilled: bool) -> None:
    h = s.get_height()
    y = h - 8
    col = (118, 82, 52) if tilled else (150, 110, 74)
    edge = (88, 58, 36)
    pygame.draw.rect(s, col, (1, y, 14, 7), border_radius=2)
    pygame.draw.rect(s, edge, (1, y, 14, 7), 1, border_radius=2)
    if tilled:
        pygame.draw.line(s, edge, (4, y + 2), (12, y + 2))
        pygame.draw.line(s, edge, (4, y + 5), (12, y + 5))


def build_plant_stages() -> list[pygame.Surface]:
    """[vazio, preparado, semente, broto, muda, arvore-com-frutos]."""
    out: list[pygame.Surface] = []

    s = pygame.Surface((16, 10), pygame.SRCALPHA); _draw_soil(s, False); out.append(s)
    s = pygame.Surface((16, 10), pygame.SRCALPHA); _draw_soil(s, True); out.append(s)

    s = pygame.Surface((16, 12), pygame.SRCALPHA)
    _draw_soil(s, True)
    pygame.draw.ellipse(s, (96, 66, 42), (5, 4, 6, 4))
    s.set_at((8, 5), (60, 40, 24))
    out.append(s)

    s = pygame.Surface((16, 15), pygame.SRCALPHA)
    _draw_soil(s, True)
    pygame.draw.line(s, cfg.LEAF_DARK, (8, 9), (8, 5))
    pygame.draw.circle(s, cfg.LEAF, (6, 5), 2)
    pygame.draw.circle(s, cfg.LEAF, (10, 5), 2)
    out.append(s)

    s = pygame.Surface((16, 22), pygame.SRCALPHA)
    _draw_soil(s, True)
    pygame.draw.line(s, cfg.LEAF_DARK, (8, 16), (8, 6), 2)
    for cx, cy, r, c in [(8, 7, 4, cfg.LEAF_DARK), (5, 8, 3, cfg.LEAF),
                         (11, 8, 3, cfg.LEAF), (8, 4, 3, cfg.LEAF_LIGHT)]:
        pygame.draw.circle(s, c, (cx, cy), r)
    out.append(s)

    s = pygame.Surface((16, 26), pygame.SRCALPHA)
    _draw_soil(s, True)
    pygame.draw.rect(s, cfg.TRUNK, (7, 14, 3, 6))
    for cx, cy, r, c in [(8, 9, 6, cfg.LEAF_DARK), (5, 8, 4, cfg.LEAF),
                         (11, 8, 4, cfg.LEAF), (8, 5, 4, cfg.LEAF_LIGHT)]:
        pygame.draw.circle(s, c, (cx, cy), r)
    for px, py in [(4, 14), (10, 15)]:
        pygame.draw.ellipse(s, cfg.FLOWER_Y, (px, py, 3, 5))
        pygame.draw.ellipse(s, (200, 140, 60), (px, py, 3, 5), 1)
    out.append(s)
    return out


# --- Fabrica de chocolate (mini-game de producao) -----------------------------

def _prop_chocolate_bench() -> pygame.Surface:
    """Bancada de producao de chocolate (34x22), com um pilao de pedra."""
    s = pygame.Surface((34, 22), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD_LIGHT, (1, 7, 32, 4))
    pygame.draw.rect(s, cfg.WOOD, (1, 11, 32, 4))
    pygame.draw.rect(s, cfg.WOOD_DARK, (1, 7, 32, 8), 1)
    pygame.draw.rect(s, cfg.WOOD_DARK, (3, 15, 3, 6))
    pygame.draw.rect(s, cfg.WOOD_DARK, (28, 15, 3, 6))
    pygame.draw.ellipse(s, (118, 116, 124), (23, 3, 9, 6))   # pilao de pedra
    pygame.draw.ellipse(s, (78, 76, 84), (25, 4, 5, 3))
    return s


def _prop_chocolate_bar() -> pygame.Surface:
    """Barra de chocolate (12x8) -- icone do HUD."""
    s = pygame.Surface((12, 8), pygame.SRCALPHA)
    pygame.draw.rect(s, (92, 56, 34), (0, 0, 12, 8), border_radius=1)
    pygame.draw.rect(s, (58, 34, 20), (0, 0, 12, 8), 1, border_radius=1)
    for x in (3, 6, 9):
        pygame.draw.line(s, (58, 34, 20), (x, 0), (x, 7))
    pygame.draw.line(s, (58, 34, 20), (0, 4), (11, 4))
    pygame.draw.rect(s, (120, 76, 48), (1, 1, 2, 2))
    return s


def _choc_item(kind: str) -> pygame.Surface:
    """Item sobre a bancada em cada etapa (14x10)."""
    s = pygame.Surface((14, 10), pygame.SRCALPHA)
    spots = [(2, 5), (5, 4), (8, 5), (4, 7), (7, 7), (10, 6)]
    if kind == "beans":          # sementes na polpa branca
        for x, y in spots:
            pygame.draw.ellipse(s, (245, 240, 230), (x, y, 4, 3))
            pygame.draw.ellipse(s, (124, 74, 42), (x + 1, y, 2, 3))
    elif kind == "fermented":    # trouxa de folha de bananeira
        pygame.draw.ellipse(s, cfg.LEAF_DARK, (2, 1, 11, 8))
        pygame.draw.ellipse(s, cfg.LEAF, (3, 2, 9, 5))
        pygame.draw.line(s, cfg.LEAF_DARK, (7, 1), (7, 8))
    elif kind == "dried":        # sementes secas
        for x, y in spots:
            pygame.draw.ellipse(s, (152, 98, 58), (x, y, 4, 4))
            pygame.draw.ellipse(s, (112, 70, 42), (x + 1, y + 1, 2, 2))
    elif kind == "roasted":      # sementes torradas (escuras)
        for x, y in spots:
            pygame.draw.ellipse(s, (92, 56, 34), (x, y, 4, 4))
            pygame.draw.ellipse(s, (58, 34, 20), (x + 1, y + 1, 2, 2))
    elif kind == "paste":        # massa de cacau
        pygame.draw.ellipse(s, (84, 50, 30), (2, 3, 11, 6))
        pygame.draw.ellipse(s, (122, 78, 50), (4, 3, 4, 2))
    return s


def build_chocolate_stages() -> list:
    """Itens por etapa: [vazio, sementes, fermentado, seco, torrado, massa]."""
    return [None, _choc_item("beans"), _choc_item("fermented"),
            _choc_item("dried"), _choc_item("roasted"), _choc_item("paste")]


def _prop_roaster() -> pygame.Surface:
    """Estacao de torra (24x20): fogo de tijolo com tabuleiro."""
    s = pygame.Surface((24, 20), pygame.SRCALPHA)
    pygame.draw.rect(s, (150, 80, 60), (2, 10, 20, 9))
    pygame.draw.rect(s, (110, 58, 42), (2, 10, 20, 9), 1)
    for x in (8, 15):
        pygame.draw.line(s, (110, 58, 42), (x, 10), (x, 18))
    pygame.draw.polygon(s, (232, 120, 40), [(8, 11), (12, 4), (16, 11)])   # fogo
    pygame.draw.polygon(s, (245, 200, 80), [(10, 11), (12, 7), (14, 11)])
    pygame.draw.ellipse(s, (92, 92, 100), (4, 1, 16, 5))                   # tabuleiro
    pygame.draw.ellipse(s, (60, 60, 68), (4, 1, 16, 5), 1)
    pygame.draw.rect(s, (60, 60, 68), (20, 2, 4, 2))                       # cabo
    return s


def _prop_mill() -> pygame.Surface:
    """Estacao de moagem (20x22): moinho de pedra com manivela."""
    s = pygame.Surface((20, 22), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD, (2, 12, 16, 9))
    pygame.draw.rect(s, cfg.WOOD_DARK, (2, 12, 16, 9), 1)
    pygame.draw.ellipse(s, (128, 126, 134), (3, 5, 14, 9))
    pygame.draw.ellipse(s, (92, 90, 98), (5, 6, 10, 6))
    pygame.draw.circle(s, (152, 150, 158), (10, 9), 3)
    pygame.draw.line(s, cfg.WOOD_DARK, (10, 9), (15, 3), 2)
    pygame.draw.circle(s, cfg.WOOD_DARK, (15, 3), 2)
    return s


def _prop_molds() -> pygame.Surface:
    """Estacao de moldagem (24x16): mesa com formas de barra."""
    s = pygame.Surface((24, 16), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD_LIGHT, (1, 4, 22, 4))
    pygame.draw.rect(s, cfg.WOOD, (1, 8, 22, 3))
    pygame.draw.rect(s, cfg.WOOD_DARK, (1, 4, 22, 7), 1)
    pygame.draw.rect(s, cfg.WOOD_DARK, (3, 11, 2, 4))
    pygame.draw.rect(s, cfg.WOOD_DARK, (19, 11, 2, 4))
    for mx in (4, 11, 18):                          # formas com chocolate
        pygame.draw.rect(s, (118, 118, 126), (mx - 1, 1, 5, 4), border_radius=1)
        pygame.draw.rect(s, (92, 56, 34), (mx, 2, 3, 2))
    return s


def _prop_stall() -> pygame.Surface:
    """Banca de venda (36x30): balcao com toldo listrado e chocolates."""
    s = pygame.Surface((36, 30), pygame.SRCALPHA)
    pygame.draw.rect(s, cfg.WOOD_DARK, (2, 6, 2, 22))
    pygame.draw.rect(s, cfg.WOOD_DARK, (32, 6, 2, 22))
    for i in range(0, 36, 6):                       # toldo listrado
        col = (206, 72, 60) if (i // 6) % 2 == 0 else (245, 240, 230)
        pygame.draw.rect(s, col, (i, 2, 6, 6))
    pygame.draw.rect(s, (160, 40, 36), (0, 8, 36, 2))
    pygame.draw.rect(s, cfg.WOOD, (2, 18, 32, 9))   # balcao
    pygame.draw.rect(s, cfg.WOOD_LIGHT, (2, 18, 32, 2))
    pygame.draw.rect(s, cfg.WOOD_DARK, (2, 18, 32, 9), 1)
    for cx in (8, 16, 24):                          # chocolates expostos
        pygame.draw.rect(s, (92, 56, 34), (cx, 14, 5, 4))
        pygame.draw.rect(s, (58, 34, 20), (cx, 14, 5, 4), 1)
    return s


def _prop_basket() -> pygame.Surface:
    """Cestinho do HUD (14x11)."""
    s = pygame.Surface((14, 11), pygame.SRCALPHA)
    pygame.draw.arc(s, (150, 108, 64), (3, 0, 8, 8), 0, 3.15, 1)   # alca
    pygame.draw.ellipse(s, (200, 154, 100), (1, 3, 12, 7))
    pygame.draw.ellipse(s, (150, 108, 64), (1, 3, 12, 7), 1)
    for x in (4, 7, 10):
        pygame.draw.line(s, (150, 108, 64), (x, 4, ), (x, 9))
    return s


def _icon_cacao() -> pygame.Surface:
    """Iconezinho de fruto de cacau (10x10) para o HUD."""
    s = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (224, 150, 60), (1, 1, 8, 8))
    pygame.draw.ellipse(s, (180, 110, 40), (1, 1, 8, 8), 1)
    pygame.draw.line(s, (180, 110, 40), (5, 1), (5, 8))
    pygame.draw.line(s, (245, 200, 110), (3, 2), (3, 7))
    return s


def build_factory_props() -> dict[str, pygame.Surface]:
    return {
        "bench": _prop_chocolate_bench(),
        "bar": _prop_chocolate_bar(),
        "cacao": _icon_cacao(),
        "roaster": _prop_roaster(),
        "mill": _prop_mill(),
        "molds": _prop_molds(),
        "stall": _prop_stall(),
        "basket": _prop_basket(),
    }