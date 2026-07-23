"""Cena do interior da palafita, decorada e dividida em comodos.

Quarto (rede, guarda-roupa) a esquerda, sala (sofa, TV, mesa do bilhete) no
centro e cozinha (fogao, bancada, cesto) a direita, separados por paredes
internas com passagem. A porta da sala leva ao quintal.
"""

from __future__ import annotations

import pygame

from .. import art
from .. import settings as cfg
from ..camera import Camera
from ..dialogue import DialogueBox
from ..fonts import game_font
from ..player import Player
from ..prop import Prop
from ..tilemap import TileMap
from .base import Scene

# Mapa da casa original (22x12). ^ topo de parede, # parede, W janela.
HOUSE_MAP = [
    "^^^WW^^^^^WW^^^^^WW^^^",
    "#......#......#......#",
    "#......#......#......#",
    "#......#......#......#",
    "#......#......#......#",
    "#....................#",
    "#....................#",
    "#......#......#......#",
    "#......#......#......#",
    "#......#......#......#",
    "#......#......#......#",
    "######################",
]

TEXTS = {
    "intro": (
        "",
        [
            "Ilha do Combú, pertinho de Belém do Pará. Esta é a sua casa de "
            "palafita!",
            "Esta construção é elevada sobre estacas de madeira para evitar que as águas do Rio Guamá invadam a residência durante as marés altas.",
            "Isso demonstra como a nossa comunidade se adaptou perfeitamente às florestas inundáveis da Amazônia!",
            "À esquerda fica o quarto; no meio, a sala; à direita, a cozinha.",
            "Aperte Z perto das coisas para observá-las. Quando quiser, saia "
            "pela porta da sala.",
        ],
    ),
    "hammock": ("Rede", [
        "A rede é a cama dos ribeirinhos: aqui você dorme embalado pelo balanço.",
        "Na Amazônia também se descansa e se recebe visita deitado nela.",
    ]),
    "wardrobe": ("Guarda-roupa", [
        "Onde ficam suas roupas. Lá no fundo, uma rede extra, dobrada, espera "
        "alguma visita.",
    ]),
    "table": ("Bilhete na mesa", [
        "'Filho, fui buscar farinha na vizinha. Começa a cuidar das mudas de "
        "cacau no quintal. Volto logo. - Mãe'",
    ]),
    "sofa": ("Sofá", [
        "Um sofá macio para descansar e ouvir as histórias dos mais velhos.",
    ]),
    "tv": ("TV", [
        "Uma TV de tubo, daquelas antigas. Está passando uma reportagem sobre a "
        "fábrica de chocolate da Dona Nena!",
    ]),
    "seedling": ("Muda de Cacau", [
        "Uma muda de cacaueiro (Theobroma cacao), árvore nativa da Amazônia.",
        "Quando pequena, gosta de sombra, por isso fica pertinho da janela, na "
        "luz suave.",
        "De seus frutos saem as sementes que viram o chocolate. Será a sua "
        "primeira plantação!",
    ]),
    "stove": ("Fogão a Lenha", [
        "O coração da cozinha: o fogão a lenha aquece a casa e prepara a comida.",
        "Aqui ganham vida o tacacá e o peixe assado na folha da bananeira.",
    ]),
    "counter": ("Bancada", [
        "A bancada com a pia. É onde se limpa o peixe e se amassa o açaí.",
    ]),
    "waterjar": ("Talha", [
        "Uma talha de barro guarda a água da casa. O barro mantém ela "
        "fresquinha o dia todo.",
    ]),
    "basket": ("Cesto de Açaí", [
        "Um cesto cheio de açaí, colhido lá no alto das palmeiras.",
        "Energia pura dos ribeirinhos: vira 'vinho' e acompanha o almoço, com "
        "farinha e peixe.",
    ]),
    "potplant": ("Plantinha", [
        "Uma plantinha de enfeite. O verde deixa a casa ribeirinha ainda mais "
        "aconchegante.",
    ]),
}


class HouseScene(Scene):
    def __init__(self, game, entry: str = "default") -> None:
        super().__init__(game)
        tiles = art.build_tiles()
        a = art.build_props()
        char = art.build_character()

        self.tilemap = TileMap(HOUSE_MAP, tiles)
        self.camera = Camera(self.tilemap.pixel_w, self.tilemap.pixel_h)

        if entry == "from_outside":
            self.player = Player(160, 148, char)
            self.player.direction = "up"
        else:
            self.player = Player(168, 88, char)

        # Decoracao "de chao/parede" (desenhada antes dos moveis e do jogador).
        self.floor_props = [
            Prop("rug", a["rug"], 30, 72),       # tapete do quarto
            Prop("rug", a["rug"], 150, 52),      # tapete da sala (sob o sofa/mesa)
            Prop("picture", a["picture"], 156, 2),   # quadro (sala)
            Prop("clock", a["clock"], 300, 2),        # relogio (cozinha)
            Prop("shelf", a["shelf"], 248, 18),       # prateleira (cozinha)
        ]
        self.props = self._make_props(a)
        self.colliders = list(self.tilemap.colliders) + [
            p.solid for p in self.props if p.solid is not None
        ]

        self.font = game_font(16)
        self.hint_font = game_font(15)
        self.dialogue = DialogueBox(self.font)
        self.camera.update(self.player.rect)

        # CORREÇÃO: A introdução só é exibida se o jogador NÃO estiver vindo do quintal
        if entry != "from_outside":
            speaker, pages = TEXTS["intro"]
            self.dialogue.open(pages, speaker)

    def _make_props(self, a: dict[str, pygame.Surface]) -> list[Prop]:
        props: list[Prop] = []

        def furn(key, x, y, solid, interactive=True, art_key=None):
            inter = solid.inflate(8, 8) if interactive else None
            props.append(Prop(key, a[art_key or key], x, y, solid, inter))

        # Quarto
        furn("hammock", 22, 34, pygame.Rect(24, 36, 28, 8))
        furn("nightstand", 84, 36, pygame.Rect(85, 40, 12, 10), interactive=False)
        furn("wardrobe", 22, 112, pygame.Rect(24, 126, 18, 14))
        furn("potplant", 88, 122, pygame.Rect(90, 132, 10, 6))
        # Sala: TV, mesa de centro e sofa agrupados (sofa de frente para a TV).
        furn("seedling", 134, 18, pygame.Rect(138, 26, 8, 7))
        furn("cabinet", 164, 20, pygame.Rect(165, 24, 28, 10), interactive=False)
        props.append(Prop("tv", a["tv"], 168, 6, None, None))  # sobre o aparador
        furn("table", 166, 40, pygame.Rect(168, 48, 12, 8))
        furn("sofa", 158, 56, pygame.Rect(160, 66, 28, 8), art_key="sofa_up")
        # Cozinha
        furn("stove", 250, 36, pygame.Rect(252, 44, 12, 7))
        furn("basket", 302, 40, pygame.Rect(304, 46, 11, 7))
        furn("counter", 246, 128, pygame.Rect(247, 132, 30, 12))
        furn("waterjar", 310, 124, pygame.Rect(312, 130, 10, 8))
        # Porta da sala
        props.append(Prop("door", a["door"], 160, 160,
                          pygame.Rect(162, 172, 12, 6), pygame.Rect(156, 162, 24, 28)))
        return props

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.fade is not None:
            return
        if event.key == pygame.K_ESCAPE:
            if self.dialogue.active:
                self.dialogue.active = False
            else:
                from .title import TitleScene
                self.game.change_scene(TitleScene(self.game))
            return
        if event.key in (pygame.K_z, pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
            if self.dialogue.active:
                self.dialogue.advance()
            else:
                self._try_interact()

    def _try_interact(self) -> None:
        prop = self._facing_prop()
        if prop is None:
            return
        if prop.name == "door":
            from .outdoor import OutdoorScene
            self.warp_to(lambda: OutdoorScene(self.game, entry="from_house"))
            return
        if prop.name in TEXTS:
            speaker, pages = TEXTS[prop.name]
            self.dialogue.open(pages, speaker)

    def _facing_prop(self) -> Prop | None:
        point = self.player.front_point()
        for p in self.props:
            if p.interact is not None and p.interact.collidepoint(point):
                return p
        return None

    def update(self, dt: float) -> None:
        if self.update_fade(dt):
            return
        if self.dialogue.active:
            self.dialogue.update(dt)
        else:
            self.player.update(dt, pygame.key.get_pressed(), self.colliders)
        self.camera.update(self.player.rect)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(cfg.BLACK)
        self.tilemap.draw(surface, self.camera)
        for deco in self.floor_props:
            deco.draw(surface, self.camera)

        drawables = [(p.sort_y, p) for p in self.props]
        drawables.append((self.player.feet.bottom, self.player))
        for _, obj in sorted(drawables, key=lambda d: d[0]):
            obj.draw(surface, self.camera)

        if not self.dialogue.active and self.fade is None:
            facing = self._facing_prop()
            if facing is not None:
                self._draw_hint(surface, facing)
        self.dialogue.draw(surface)
        self.draw_fade(surface)

    def _draw_hint(self, surface: pygame.Surface, prop: Prop) -> None:
        bx = prop.solid.centerx - self.camera.x - 5
        by = prop.y - self.camera.y - 11
        pygame.draw.rect(surface, cfg.DLG_BG, (bx - 1, by - 1, 11, 11), border_radius=2)
        pygame.draw.rect(surface, cfg.DLG_BORDER, (bx - 1, by - 1, 11, 11), 1, border_radius=2)
        z = self.hint_font.render("Z", True, cfg.DLG_TEXT)
        surface.blit(z, (bx + 1, by - 1))