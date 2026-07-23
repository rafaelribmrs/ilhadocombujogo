"""Mapa em tiles, pre-renderizado numa unica Surface, com colisores."""

from __future__ import annotations

import pygame

from . import settings as cfg
from .camera import Camera


class TileMap:
    # caractere -> (nome do tile, solido?)
    LEGEND: dict[str, tuple[str, bool]] = {
        ".": ("floor", False),
        "#": ("wall", True),
        "^": ("wall_top", True),
        "W": ("window", True),
        "D": ("floor", False),  # piso da porta (a porta em si e um prop)
    }

    def __init__(
        self,
        rows: list[str],
        tiles: dict[str, pygame.Surface],
        legend: dict[str, tuple[str, bool]] | None = None,
    ) -> None:
        self.rows = rows
        self.tiles = tiles
        self.legend = legend or self.LEGEND
        self.tile = cfg.TILE_SIZE
        self.cols = max(len(r) for r in rows)
        self.rows_n = len(rows)
        self.pixel_w = self.cols * self.tile
        self.pixel_h = self.rows_n * self.tile
        self.colliders: list[pygame.Rect] = []
        self.surface = self._prerender()

    def _prerender(self) -> pygame.Surface:
        surf = pygame.Surface((self.pixel_w, self.pixel_h))
        surf.fill(cfg.BLACK)
        default_name = next(iter(self.tiles))  # 1o tile (floor/grass) como fallback
        for ty, row in enumerate(self.rows):
            for tx, ch in enumerate(row):
                name, solid = self.legend.get(ch, (default_name, False))
                surf.blit(self.tiles[name], (tx * self.tile, ty * self.tile))
                if solid:
                    self.colliders.append(
                        pygame.Rect(tx * self.tile, ty * self.tile, self.tile, self.tile)
                    )
        return surf

    def draw(self, target: pygame.Surface, camera: Camera) -> None:
        target.blit(self.surface, (-camera.x, -camera.y))
