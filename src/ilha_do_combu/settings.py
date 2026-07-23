"""Constantes globais do jogo.

A resolucao interna imita a do Game Boy Advance (240x160), plataforma de
Pokemon FireRed e Zelda: The Minish Cap. Tudo e desenhado nessa resolucao
e depois ampliado por um fator inteiro para a janela, garantindo um visual
pixel-perfect (sem borrar os pixels).
"""

# Resolucao nativa (estilo GBA) -------------------------------------------------
NATIVE_WIDTH = 240
NATIVE_HEIGHT = 160
SCALE = 4  # fator de ampliacao para a janela
WINDOW_WIDTH = NATIVE_WIDTH * SCALE
WINDOW_HEIGHT = NATIVE_HEIGHT * SCALE

TILE_SIZE = 16  # tiles 16x16, padrao dos JRPGs de GBA/SNES
FPS = 60

TITLE = "Ilha do Combú"            # titulo provisorio (o PDF deixa o nome em aberto)
SUBTITLE = "A Semente do Cacau"

# Paleta paraense / amazonica ---------------------------------------------------
# Tons quentes de madeira, verdes de mata e o azul do rio.
BLACK = (26, 20, 16)
WHITE = (245, 240, 230)

# Madeira da palafita
WOOD_DARK = (92, 58, 33)
WOOD = (124, 82, 47)
WOOD_LIGHT = (158, 110, 67)
WOOD_HILIGHT = (186, 138, 92)

# Parede / palha
WALL = (74, 52, 33)
WALL_LIGHT = (96, 70, 46)

# Vegetacao
LEAF_DARK = (34, 92, 48)
LEAF = (58, 132, 64)
LEAF_LIGHT = (96, 170, 86)

# Rio / ceu pela janela
SKY = (140, 198, 214)
RIVER = (74, 142, 150)
RIVER_DARK = (52, 112, 122)

# UI / caixa de dialogo (estilo Pokemon Emerald: caixa clara, borda azul-marinho)
UI_BG = (38, 28, 22)
UI_BORDER = (214, 178, 120)
UI_TEXT = (245, 240, 230)

DLG_BG = (248, 248, 240)        # interior quase branco
DLG_BORDER = (40, 48, 96)       # azul-marinho (borda externa)
DLG_BORDER2 = (96, 128, 200)    # azul claro (linha interna)
DLG_TEXT = (40, 40, 64)         # texto azul-escuro
DLG_SHADOW = (170, 180, 198)    # sombra do texto

# Vegetacao do overworld (estilo Emerald)
GRASS = (104, 168, 88)
GRASS_DARK = (72, 136, 72)
GRASS_LIGHT = (152, 200, 112)
PATH = (206, 180, 126)
PATH_DARK = (170, 142, 96)
WATER = (88, 160, 216)
WATER_DARK = (64, 128, 200)
WATER_LIGHT = (152, 208, 240)
TRUNK = (110, 74, 44)
FLOWER_R = (224, 96, 96)
FLOWER_Y = (240, 208, 96)
