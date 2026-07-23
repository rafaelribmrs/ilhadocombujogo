"""Renderiza todos os sprites num PNG ampliado para inspecao visual."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from ilha_do_combu import art  # noqa: E402

SCALE = 6
BG = (60, 60, 70)
GRID = (90, 90, 100)

chars = art.build_character()
tiles = art.build_tiles()
props = art.build_props()

# layout: linhas de itens
canvas = pygame.Surface((760, 560))
canvas.fill(BG)

font = pygame.font.Font(None, 16)


def blit_label(x, y, text):
    canvas.blit(font.render(text, True, (230, 230, 230)), (x, y))


def blit_sprite(surf, x, y):
    w, h = surf.get_size()
    big = pygame.transform.scale(surf, (w * SCALE, h * SCALE))
    pygame.draw.rect(canvas, GRID, (x - 1, y - 1, w * SCALE + 2, h * SCALE + 2), 1)
    canvas.blit(big, (x, y))
    return w * SCALE


# Personagem: cada direcao com seus 4 quadros
y = 24
blit_label(8, y - 16, "Personagem (down / up / left / right)")
for direction in ("down", "up", "left", "right"):
    x = 8
    blit_label(x, y + 20, direction)
    x = 60
    for frame in chars[direction]:
        x += blit_sprite(frame, x, y) + 8
    y += 16 * SCALE + 10

# Tiles
ty = 24
tx = 470
blit_label(tx, ty - 16, "Tiles")
for name, surf in tiles.items():
    blit_label(tx, ty + 18, name)
    blit_sprite(surf, tx + 70, ty)
    ty += 16 * SCALE + 6

# Props
py = 24
px = 470
# coloca props abaixo dos tiles, em outra coluna se couber
py = 360
blit_label(8, py - 4, "Objetos")
px = 8
py = 380
for name, surf in props.items():
    w = blit_sprite(surf, px, py)
    blit_label(px, py - 14, name)
    px += w + 16
    if px > 640:
        px = 8
        py += 100

out = os.path.join(os.path.dirname(__file__), "preview_art.png")
pygame.image.save(canvas, out)
print("saved", out)
