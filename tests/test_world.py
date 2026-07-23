"""Testes do mapa, colisao do jogador e dialogo."""

from collections import defaultdict

import pygame

from ilha_do_combu import art
from ilha_do_combu.dialogue import DialogueBox
from ilha_do_combu.player import Player
from ilha_do_combu.tilemap import TileMap

SIMPLE_MAP = [
    "####",
    "#..#",
    "#..#",
    "####",
]


def test_tilemap_dimensions_and_colliders():
    tm = TileMap(SIMPLE_MAP, art.build_tiles())
    assert tm.pixel_w == 4 * 16
    assert tm.pixel_h == 4 * 16
    # 16 tiles, 4 internos sao piso -> 12 solidos
    assert len(tm.colliders) == 12


def test_player_blocked_by_wall():
    frames = art.build_character()
    tm = TileMap(SIMPLE_MAP, art.build_tiles())
    player = Player(16, 16, frames)  # dentro da sala (tile 1,1)
    keys = defaultdict(bool)         # qualquer tecla -> False por padrao
    keys[pygame.K_RIGHT] = True
    for _ in range(120):  # tenta atravessar a parede direita por 2s
        player.update(1 / 60, keys, tm.colliders)
    # a parede direita (coluna 3) comeca em x = 48; os pes nao a cruzam.
    assert player.feet.right <= 48


class _FakeGame:
    def __init__(self):
        self.scene = None

    def change_scene(self, scene):
        self.scene = scene


def test_door_warps_house_to_outdoor():
    from ilha_do_combu.scenes.house import HouseScene
    from ilha_do_combu.scenes.outdoor import OutdoorScene

    game = _FakeGame()
    house = HouseScene(game, entry="from_outside")  # sem dialogo de intro
    house.fade = None                               # simula o fim do fade de entrada
    house.player.x, house.player.y = 160, 144       # de frente para a porta (sala)
    house.player.direction = "down"

    house._try_interact()
    assert house.fade is not None                   # iniciou o fade de saida

    for _ in range(120):
        house.update_fade(1 / 60)
        if game.scene is not None:
            break
    assert isinstance(game.scene, OutdoorScene)


def test_plot_full_cycle():
    from ilha_do_combu import art
    from ilha_do_combu.plot import Plot, GROW_TIME, EMPTY, TILLED, TREE

    stages = art.build_plant_stages()
    plot = Plot(0, 0, stages)
    assert plot.stage == EMPTY
    plot.act()                       # preparar a terra
    plot.act()                       # plantar a semente
    _, _, harvested = plot.act()     # regar -> broto
    assert not harvested
    for _ in range(2):               # cresce sozinho: broto -> muda -> arvore
        plot.update(GROW_TIME)
    assert plot.stage == TREE
    _, _, harvested = plot.act()     # colher
    assert harvested
    assert plot.stage == TILLED      # canteiro livre para replantar


def test_hud_and_basket_reveal():
    from ilha_do_combu.scenes.outdoor import OutdoorScene
    from ilha_do_combu.plot import TREE

    class _Game:
        def change_scene(self, scene):
            pass

    sc = OutdoorScene(_Game())
    assert not sc.hud_visible and not sc.has_basket
    plot = sc.plots[0]
    sc.player.x, sc.player.y, sc.player.direction = plot.x, plot.y + 20, "up"

    sc.dialogue.active = False
    sc._try_interact()                 # preparar a terra (ainda sem HUD)
    assert not sc.hud_visible
    sc.dialogue.active = False
    sc._try_interact()                 # plantar -> revela o HUD
    assert sc.hud_visible
    assert not sc.has_basket           # ainda nao colheu

    plot.stage = TREE
    sc.dialogue.active = False
    sc._try_interact()                 # colher -> cesto na mao
    assert sc.has_basket
    assert sc.harvested == 1


def test_chocolate_production_line():
    from ilha_do_combu.scenes.outdoor import OutdoorScene

    class _Game:
        def change_scene(self, scene):
            pass

    sc = OutdoorScene(_Game())
    sc.harvested = 3

    def make_one_chocolate():
        sc.prep.act(sc)   # quebra (consome 1 cacau)
        sc.prep.act(sc)   # fermenta
        sc.prep.act(sc)   # seca
        sc.prep.act(sc)   # pega -> carrega "dried"
        assert sc.carrying == "dried"
        by_name = {s.name: s for s in sc.stations}
        sc._station_act(by_name["torra"])
        assert sc.carrying == "roasted"
        sc._station_act(by_name["moagem"])
        assert sc.carrying == "paste"
        sc._station_act(by_name["moldagem"])

    make_one_chocolate()
    assert sc.carrying is None and sc.basket == 1 and sc.harvested == 2
    make_one_chocolate()
    make_one_chocolate()
    assert sc.basket == 3
    banca = {s.name: s for s in sc.stations}["banca"]
    sc._station_act(banca)
    assert sc.sold == 3 and sc.basket == 0

    # vender UM unico chocolate tambem conta: o total soma 1
    sc.harvested = 1
    make_one_chocolate()
    assert sc.basket == 1
    sc._station_act(banca)
    assert sc.sold == 4 and sc.basket == 0


def test_dialogue_wraps_and_advances():
    font = pygame.font.Font(None, 14)
    box = DialogueBox(font)
    long_text = "palavra " * 40
    box.open([long_text, "fim"])
    assert box.active
    # a primeira pagina deve quebrar em varias linhas
    assert len(box._pages[0]) > 1
    # texto longo e paginado: avanca ate fechar
    for _ in range(40):
        box.update(10.0)
        box.advance()
        if not box.active:
            break
    assert not box.active
