"""Gera o icone do jogo (ilha_do_combu.ico) a partir de arte desenhada."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
from PIL import Image  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

S = 256
s = pygame.Surface((S, S), pygame.SRCALPHA)

# fundo verde arredondado (grama da ilha)
pygame.draw.rect(s, (104, 168, 88), (6, 6, S - 12, S - 12), border_radius=44)
pygame.draw.rect(s, (152, 200, 112), (6, 6, S - 12, S - 12), 0, border_radius=44)
pygame.draw.rect(s, (104, 168, 88), (6, 70, S - 12, S - 76), border_bottom_left_radius=44,
                 border_bottom_right_radius=44)
pygame.draw.rect(s, (72, 136, 72), (6, 6, S - 12, S - 12), 8, border_radius=44)

# barra de chocolate (elemento principal), levemente inclinada
bar = pygame.Surface((150, 104), pygame.SRCALPHA)
pygame.draw.rect(bar, (110, 70, 42), (0, 0, 150, 104), border_radius=14)
for x in range(0, 151, 50):
    pygame.draw.line(bar, (74, 44, 26), (x, 0), (x, 104), 7)
pygame.draw.line(bar, (74, 44, 26), (0, 52), (150, 52), 7)
pygame.draw.rect(bar, (74, 44, 26), (0, 0, 150, 104), 9, border_radius=14)
pygame.draw.rect(bar, (148, 98, 60), (12, 9, 32, 16), border_radius=4)
bar = pygame.transform.rotate(bar, -10)
s.blit(bar, (S // 2 - bar.get_width() // 2 + 6, S // 2 - bar.get_height() // 2 + 18))

# fruto de cacau no canto superior
pygame.draw.ellipse(s, (228, 152, 62), (30, 26, 58, 78))
for i in range(4):
    pygame.draw.line(s, (190, 116, 44), (44 + i * 11, 34), (44 + i * 11, 96), 3)
pygame.draw.ellipse(s, (190, 116, 44), (30, 26, 58, 78), 5)
pygame.draw.ellipse(s, (248, 206, 120), (40, 36, 12, 26))

out_png = os.path.join(os.path.dirname(__file__), "..", "icon_src.png")
pygame.image.save(s, out_png)

img = Image.open(out_png).convert("RGBA")
ico = os.path.join(os.path.dirname(__file__), "..", "ilha_do_combu.ico")
img.save(ico, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("saved", os.path.abspath(ico))
