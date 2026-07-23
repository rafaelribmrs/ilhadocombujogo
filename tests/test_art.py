"""Testes da arte procedural."""

import pygame

from ilha_do_combu import art

MAGENTA = (255, 0, 255)


def _has_magenta(surf: pygame.Surface) -> bool:
    """True se houver pixel magenta opaco (indica caractere fora da paleta)."""
    w, h = surf.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, *a = surf.get_at((x, y))
            if (r, g, b) == MAGENTA and (not a or a[0] > 0):
                return True
    return False


def test_character_has_all_directions_and_frames():
    char = art.build_character()
    assert set(char) == {"down", "up", "left", "right"}
    for direction, frames in char.items():
        assert len(frames) == 4, direction
        for frame in frames:
            assert frame.get_size() == (16, 24)  # sprite alto estilo Emerald


def test_no_sprite_uses_palette_error_color():
    surfaces = []
    for frames in art.build_character().values():
        surfaces.extend(frames)
    surfaces.extend(art.build_tiles().values())
    surfaces.extend(art.build_props().values())
    surfaces.extend(art.build_outdoor_tiles().values())
    surfaces.extend(art.build_outdoor_props().values())
    for surf in surfaces:
        assert not _has_magenta(surf), "sprite tem pixel magenta (caractere invalido no grid)"


def test_tiles_are_tile_sized():
    for tiles in (art.build_tiles(), art.build_outdoor_tiles()):
        for name, surf in tiles.items():
            assert surf.get_size() == (16, 16), name
