"""Renderiza estados do jogo em PNGs para inspecao visual (headless)."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from ilha_do_combu import settings as cfg  # noqa: E402
from ilha_do_combu.game import Game  # noqa: E402
from ilha_do_combu.scenes.title import TitleScene  # noqa: E402
from ilha_do_combu.scenes.house import HouseScene  # noqa: E402
from ilha_do_combu.scenes import outdoor  # noqa: E402
from ilha_do_combu.scenes.outdoor import OutdoorScene  # noqa: E402

game = Game()
SC = 3
HERE = os.path.dirname(__file__)


def save(name):
    big = pygame.transform.scale(
        game.native, (cfg.NATIVE_WIDTH * SC, cfg.NATIVE_HEIGHT * SC)
    )
    pygame.image.save(big, os.path.join(HERE, name))
    print("saved", name)


def shot(scene, name, setup=None):
    scene.fade = None  # desliga o fade para capturar a cena
    if setup:
        setup(scene)
    scene.camera.update(scene.player.rect)
    scene.draw(game.native)
    save(name)


def shot_title():
    s = TitleScene(game)
    s.fade = None
    s.draw(game.native)
    save("shot_title.png")


shot_title()
shot(HouseScene(game), "shot_house_dialog.png", lambda s: s.dialogue.update(3.0))


def _explore(s):
    s.dialogue.active = False
    s.player.x, s.player.y, s.player.direction = 140, 148, "up"  # de frente p/ a mesa


shot(HouseScene(game), "shot_house_explore.png", _explore)
shot(OutdoorScene(game), "shot_outdoor.png")


def _outdoor_dialog(s):
    s.player.x, s.player.y, s.player.direction = 150, 64, "up"
    speaker, pages = outdoor.TEXTS["cacao_tree"]
    s.dialogue.open(pages, speaker)
    s.dialogue.update(4.0)


shot(OutdoorScene(game), "shot_outdoor_dialog.png", _outdoor_dialog)


def _garden(s):
    from ilha_do_combu.plot import SEED, MUDA, TREE
    for plot, st in zip(s.plots, (SEED, MUDA, TREE)):
        plot.stage = st
    s.harvested = 3
    s.hud_visible = True
    s.has_basket = True
    s.player.x, s.player.y, s.player.direction = 154, 96, "up"


shot(OutdoorScene(game), "shot_garden.png", _garden)


def _factory(s):
    s.harvested = 2
    s.carrying = "roasted"   # carregando algo -> mostra a bolha
    s.basket = 2
    s.sold = 3
    s.hud_visible = True
    s.has_basket = True
    s.player.x, s.player.y, s.player.direction = 168, 140, "up"  # de frente p/ moagem


shot(OutdoorScene(game), "shot_factory.png", _factory)


def shot_house_full():
    """Casa inteira, sem recorte de camera, para conferir a decoracao."""
    class _Cam:
        x = 0
        y = 0

    h = HouseScene(game)
    h.dialogue.active = False
    cam = _Cam()
    full = pygame.Surface((h.tilemap.pixel_w, h.tilemap.pixel_h))
    full.fill(cfg.BLACK)
    h.tilemap.draw(full, cam)
    for deco in h.floor_props:
        deco.draw(full, cam)
    for _, o in sorted([(p.sort_y, p) for p in h.props], key=lambda d: d[0]):
        o.draw(full, cam)
    big = pygame.transform.scale(full, (full.get_width() * 2, full.get_height() * 2))
    pygame.image.save(big, os.path.join(HERE, "shot_house_full.png"))
    print("saved shot_house_full.png")


shot_house_full()
