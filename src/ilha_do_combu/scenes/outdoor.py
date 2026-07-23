"""Cena do quintal: overworld estilo Pokemon Emerald com os 6 canteiros de areia livres."""

from __future__ import annotations

import pygame

from .. import art
from .. import settings as cfg
from ..camera import Camera
from ..dialogue import DialogueBox
from ..factory import PrepBench, Station
from ..fonts import game_font
from ..player import Player
from ..prop import Prop  
from ..tilemap import TileMap
from .base import Scene

from ilha_do_combu.plot import Plot


# MAPA CORRIGIDO: Linhas da água completadas com 24 caracteres exatos (sem buraco preto)
OUTDOOR_MAP = [
    "vffffffffffffffffffffffv",
    "vggggghijklmnopqrstggggv",
    "vgTTgggggggggggggggggggv",
    "vgTTgggggggggggggggggggv",
    "vggggggggggggggggggggggv",
    "vggggggggggggggggggggggv",
    "vggggggggggggggggggggggv",
    "vggggggggggggggggggggggv",
    "vggggggggggggggggggggggv",
    "vggggggggggggggggggggggv",
    "vggggggggggggggggggggggv",
    "wwwwxxxxxxxxxxxxxxxxwwww",
    "wwwwxxxxxxxxxxxxxxxxwwwW",
]

OUTDOOR_LEGEND = {
    "g": ("grass", False),
    "T": ("grass_tall", False),
    "w": ("water", True),
    "x": ("water", True),
    "W": ("water", True),
    "f": ("fence", True),      
    "v": ("fence_v", True),    
}

TEXTS = {
    "tree": ("Árvore", ["Uma árvore nativa fazendo sombra no quintal."]),
}


class OutdoorScene(Scene):
    def __init__(self, game, entry: str = "from_house", restaurar_barras: bool = False) -> None:
        super().__init__(game)
        tiles = art.build_outdoor_tiles()
        
        if "fence" in tiles and "fence_v" not in tiles:
            tiles["fence_v"] = pygame.transform.rotate(tiles["fence"], 90)
            
        pa = art.build_outdoor_props()
        fa = art.build_factory_props()
        char = art.build_character()
        choc = art.build_chocolate_stages()

        self.tilemap = TileMap(OUTDOOR_MAP, tiles, OUTDOOR_LEGEND)
        self.camera = Camera(self.tilemap.pixel_w, self.tilemap.pixel_h)

        # Posicionamento da palafita e spawn ajustados fora do HUD
        if entry == "from_boat":
            self.player = Player(110, 150, char)
            self.player.direction = "up"
            self.game.saved_bars = getattr(game, "saved_bars", 0)
            self.game.money = getattr(game, "money", 0)
            self.game.harvested_seeds = getattr(game, "harvested_seeds", 0)
            self.game.save_game()
        elif entry == "from_house":
            self.player = Player(126, 52, char)  
            self.player.direction = "down"
        elif entry == "from_harvest":
            self.player = Player(220, 46, char)
        else:
            self.player = Player(126, 52, char)  
            self.player.direction = "down"

        self.equipped_tool: str | None = None 
        self.props = self._make_props(pa)

        # 6 Canteiros livres organizados sequencialmente no lado direito e longe da cerca
        self.plots = [
            Plot(225, 45, art.build_plant_stages(), pa["cacao_tree"]),
            Plot(270, 45, art.build_plant_stages(), pa["cacao_tree"]),
            Plot(315, 45, art.build_plant_stages(), pa["cacao_tree"]),
            Plot(225, 80, art.build_plant_stages(), pa["cacao_tree"]),
            Plot(270, 80, art.build_plant_stages(), pa["cacao_tree"]),
            Plot(315, 80, art.build_plant_stages(), pa["cacao_tree"])
        ]

        self.prep = PrepBench(40, 116, fa["bench"], choc)
        self.stations = [
            Station("torra", "Torra", 112, 118, fa["roaster"]),
            Station("moagem", "Moagem", 168, 116, fa["mill"]),
            Station("moldagem", "Moldagem", 216, 120, fa["molds"]),
            Station("banca", "Banca", 264, 112, fa["stall"]),
        ]

        self.harvested = getattr(game, "harvested_seeds", 0)
        self.carrying = None     
        self.basket = 0                       
        self.sold = 3 if restaurar_barras else getattr(game, "saved_bars", 0)
        
        # CORREÇÃO: Resgata o dinheiro total do state global do jogo para exibição local
        self.money = getattr(game, "money", 0)
        
        self.carry_icons = {"dried": choc[3], "roasted": choc[4], "paste": choc[5]}
        self.cacao_icon = fa["cacao"]
        self.bar_icon = fa["bar"]
        
        self.hud_visible = True              
        self.has_basket = False               

        self.colliders = list(self.tilemap.colliders)
        self.colliders += [p.solid for p in self.props if p.solid is not None]
        self.colliders.append(self.prep.solid)
        self.colliders += [st.solid for st in self.stations]

        self.font = game_font(16)
        self.label_font = game_font(15)
        self.hint_font = game_font(15)
        self.small_font = game_font(13)
        self.dialogue = DialogueBox(self.font)
        self.camera.update(self.player.rect)

        if entry == "from_boat":
            self.dialogue.open(["O seu progresso foi salvo automaticamente com sucesso!"], "Sistema")

    def _make_props(self, a: dict[str, pygame.Surface]) -> list[Prop]:
        props: list[Prop] = []
        
        # Altura do colisor solid aumentada para bloquear o jogador na base da casa
        props.append(Prop("house", a["house_exterior"], 110, -6,
                          solid=pygame.Rect(110, 14, 48, 34),
                          interact=pygame.Rect(120, 24, 28, 20)))

        # Flores decorativas do cenário
        for fx, fy in [(70, 56), (195, 60)]:
            props.append(Prop("flowers", a["flowers"], fx, fy))

        # Canoa rabeta ancorada na água
        barco_surf = a.get("boat", a["flowers"]) 
        props.append(Prop("boat", barco_surf, 110, 176,
                          solid=pygame.Rect(110, 176, 42, 12),
                          interact=pygame.Rect(110, 162, 42, 20)))

        # Bancada de ferramentas para equipar enxada, sementes e regador
        props.append(Prop("tool_bench", a["flowers"], 26, 56,
                          solid=pygame.Rect(26, 56, 34, 12),
                          interact=pygame.Rect(26, 46, 34, 24)))

        return props

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.fade is not None:
            return

        for plot in self.plots:
            if plot.minigame_active:
                plot.handle_minigame_input(event.key, self.dialogue, self)
                return

        if event.key == pygame.K_ESCAPE and self.dialogue.active:
            self.dialogue.active = False
            return
        
        prop = self._facing_prop()
        if prop is not None and prop.name == "tool_bench":
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.equipped_tool = "enxada"
                self.dialogue.open(["Você pegou a ENXADA da mesa!"], "Inventário")
                return
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.equipped_tool = "semente"
                self.dialogue.open(["Você pegou as SEMENTES DE CACAU da mesa!"], "Inventário")
                return
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.equipped_tool = "regador"
                self.dialogue.open(["Você pegou o REGADOR da mesa!"], "Inventário")
                return

        if event.key in (pygame.K_z, pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
            if self.dialogue.active:
                self.dialogue.advance()
            else:
                self._try_interact()

    def _try_interact(self) -> None:
        point = self.player.front_point()
        prop = self._facing_prop()

        if prop is not None and prop.name == "tool_bench":
            if self.equipped_tool is not None:
                pages = [f"Você guardou o(a) {self.equipped_tool.upper()} de volta na bancada."]
                self.equipped_tool = None
                self.dialogue.open(pages, "Bancada")
            else:
                pages = [
                    "Escolha a ferramenta digitando o número no teclado:\n"
                    " [ 1 ] Equipar ENXADA\n"
                    " [ 2 ] Equipar SEMENTES\n"
                    " [ 3 ] Equipar REGADOR"
                ]
                self.dialogue.open(pages, "Bancada")
            return

        for plot in self.plots:
            if plot.interact.collidepoint(point):
                if plot.stage == 0:
                    if self.equipped_tool == "enxada":
                        plot.stage = 1 
                        pages = ["Você usou a enxada para preparar a terra. O solo ribeirinho ficou bem fofo!"]
                    else:
                        pages = ["A terra está dura e intocada. Busque a ENXADA para arar o canteiro."]
                    self.dialogue.open(pages, "Canteiro")
                    return
                
                elif plot.stage == 1:
                    if self.equipped_tool == "semente":
                        plot.stage = 2 
                        pages = ["Você plantou as sementes de cacau selecionadas na terra preparada.",
                                 "Etapa seguinte: Traga o REGADOR para molhar a plantação e iniciar o crescimento!"]
                    else:
                        pages = ["A terra já está arada. Traga as SEMENTES de cacau para plantar!"]
                    self.dialogue.open(pages, "Canteiro")
                    return
                
                elif plot.stage == 2 or plot.stage == 3:
                    if plot.stage == 2 and self.equipped_tool == "regador":
                        plot.stage = 3
                        pages = ["Você regou a semente! Uma barra de progresso indica o crescimento do cacaueiro de 10 segundos."]
                    else:
                        if plot.stage == 2:
                            pages = ["As sementes estão sob a terra seca. Equipe o REGADOR para que comecem a brotar!"]
                        else:
                            pages = ["O cacaueiro está se desenvolvendo de forma sustentável sob o clima da Amazônia."]
                    self.dialogue.open(pages, "Canteiro")
                    return
                
                elif plot.stage == 4:
                    from ilha_do_combu.scenes.harvest import HarvestScene
                    self.warp_to(lambda: HarvestScene(self.game, parent_plot=plot))
                    return

        if self.prep.interact.collidepoint(point):
            speaker, pages = self.prep.act(self)
            self.dialogue.open(pages, speaker)
            return
        for st in self.stations:
            if st.interact.collidepoint(point):
                speaker, pages = self._station_act(st)
                self.dialogue.open(pages, speaker)
                return
        if prop is None:
            return
        
        if prop.name == "house":
            from .house import HouseScene
            self.warp_to(lambda: HouseScene(self.game, entry="from_outside"))
            return
        
        if prop.name == "boat":
            if self.sold > 0:
                self.game.saved_bars = self.sold
                self.sold = 0 
                from .river import RiverScene
                self.warp_to(lambda: RiverScene(self.game, direction="ida", bars_to_save=self.game.saved_bars))
            else:
                pages = [
                    "Uma canoa motorizada (rabeta) ancorada no Rio Guamá.",
                    "Você precisa estocar chocolates na BANCA antes de pegar o barco para ir à UFPA!"
                ]
                self.dialogue.open(pages, "Barco")
            return

        if prop.name in TEXTS:
            speaker, pages = TEXTS[prop.name]
            self.dialogue.open(pages, speaker)

    def _station_act(self, st: Station) -> tuple[str, list[str]]:
        bytes = self.carrying
        if st.name == "torra":
            if bytes == "dried":
                self.carrying = "roasted"
                return ("Torra", ["Você torrou as sementes no fogo! Leve para a MOAGEM."])
            return ("Torra", ["Aqui se torram as sementes SECAS. Prepare-as na bancada primeiro."])
        if st.name == "moagem":
            if bytes == "roasted":
                self.carrying = "paste"
                return ("Moagem", ["Você moeu no moinho: virou uma massa de cacau brilhante! Leve para a MOLDAGEM."])
            return ("Moagem", ["Aqui se moem as sementes TORRADAS. Torre-as primeiro!"])
        if st.name == "moldagem":
            if bytes == "paste":
                self.carrying = None
                self.basket += 1
                return ("Moldagem", [f"Você moldou uma barra de chocolate! (Mão: {self.basket})",
                                     "LEVE ATÉ A BANCA PARA ARMAZENAR NO ESTOQUE."])
            return ("Moldagem", ["Aqui se molda a MASSA de cacau. Moa as sementes primeiro!"])
        
        if st.name == "banca":
            if self.basket >= 1:
                n = self.basket
                self.sold += n
                self.basket = 0
                self.has_basket = False  
                palavra = "barra" if n == 1 else "barras"
                return ("Banca de Estoque", [
                    f"Você guardou {n} {palavra} de chocolate na banca!",
                    f"Estoque total acumulado: {self.sold} barras.",
                    "Tudo pronto! Pega a rabeta na beira do rio para ir vender na UFPA!"
                ])
            return ("Banca de Estoque", [f"Você não possui barras na mão. Estoque atual: {self.sold} barras."])

        return ("Estação", ["Ação indisponível."])

    def update(self, dt: float) -> None:
        if self.update_fade(dt):
            return
        for plot in self.plots:
            plot.update(dt)
        if self.dialogue.active:
            self.dialogue.update(dt)
        else:
            self.player.update(dt, pygame.key.get_pressed(), self.colliders)
        self.camera.update(self.player.rect)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(cfg.BLACK)
        self.tilemap.draw(surface, self.camera)

        drawables = [(p.sort_y, p) for p in self.props]
        drawables += [(p.sort_y, p) for p in self.plots]
        drawables.append((self.prep.sort_y, self.prep))
        drawables += [(st.sort_y, st) for st in self.stations]
        drawables.append((self.player.feet.bottom, self.player))
        for _, obj in sorted(drawables, key=lambda d: d[0]):
            obj.draw(surface, self.camera)
            
            if obj is self.player:
                if self.basket > 0:
                    self._draw_held_bar(surface)
                if self.equipped_tool is not None:
                    self._draw_tool_on_player(surface)

        if not self.dialogue.active and self.fade is None:
            self._draw_labels(surface)
            self._draw_facing_hint(surface)
        self._draw_carry(surface)
        self._draw_hud(surface)
        self.dialogue.draw(surface)
        self.draw_fade(surface)

    def _draw_tool_on_player(self, surface: pygame.Surface) -> None:
        px = int(self.player.x) - self.camera.x
        py = int(self.player.y) - self.camera.y
        if self.equipped_tool == "enxada":
            pygame.draw.rect(surface, (160, 160, 160), (px + 11, py + 12, 3, 2))
            pygame.draw.line(surface, (130, 90, 60), (px + 12, py + 6), (px + 12, py + 12), 1)
        elif self.equipped_tool == "semente":
            pygame.draw.circle(surface, (90, 50, 20), (px + 12, py + 8), 1)
        elif self.equipped_tool == "regador":
            pygame.draw.rect(surface, (40, 100, 180), (px + 11, py + 6, 4, 4), border_radius=1)
            pygame.draw.line(surface, (20, 60, 140), (px + 15, py + 7), (px + 18, py + 7), 1)

    def _draw_held_bar(self, surface: pygame.Surface) -> None:
        px = int(self.player.x) - self.camera.x
        py = int(self.player.y) - self.camera.y
        for i in range(min(self.basket, 3)):
            pygame.draw.rect(surface, (58, 34, 20), (px + 11, py + 7 - (i * 2), 5, 3))
            pygame.draw.rect(surface, (35, 18, 8), (px + 11, py + 7 - (i * 2), 5, 3), 1)

    def _draw_carry(self, surface: pygame.Surface) -> None:
        if self.carrying is None:
            return
        icon = self.carry_icons[self.carrying]
        iw, ih = icon.get_size()
        cx = int(self.player.x) + 8 - self.camera.x
        bottom = int(self.player.y) - 9 - self.camera.y
        box = pygame.Rect(cx - iw // 2 - 2, bottom - ih - 2, iw + 4, ih + 4)
        pygame.draw.rect(surface, cfg.DLG_BG, box, border_radius=2)
        pygame.draw.rect(surface, cfg.DLG_BORDER, box, 1, border_radius=2)
        surface.blit(icon, (box.x + 2, box.y + 2))

    def _draw_hud(self, surface: pygame.Surface) -> None:
        if not self.hud_visible:                   
            return
            
        # CORREÇÃO: Adicionada a terceira linha contendo o dinheiro acumulado
        rows = [
            (self.cacao_icon, f"Sementes: {self.harvested}"),
            (self.bar_icon, f"Banca: {self.sold}"),
            (None, f"Saldo: R${self.money}")
        ] 
        f = self.small_font
        lh = f.get_height()
        row_h = max(lh, 11)
        
        # CORREÇÃO: Dimensões da caixa ajustadas (altura expandida para 3x linhas e largura para 105)
        box = pygame.Rect(3, 3, 105, row_h * 3 + 4)
        DialogueBox._draw_frame(surface, box)
        y = box.y + 2
        for icon, txt in rows:
            if icon is not None:
                ix = box.x + 2 + (14 - icon.get_width()) // 2
                surface.blit(icon, (ix, y + (row_h - icon.get_height()) // 2))
            else:
                # Desenha uma moedinha dourada procedural em pixel-art no local do ícone ausente
                cx = box.x + 8
                cy = y + row_h // 2
                pygame.draw.circle(surface, (255, 215, 0), (cx, cy), 4)
                pygame.draw.circle(surface, (150, 110, 10), (cx, cy), 4, 1)
                
            surface.blit(f.render(txt, True, cfg.DLG_TEXT), (box.x + 18, y + (row_h - lh) // 2))
            y += row_h

    def _draw_labels(self, surface: pygame.Surface) -> None:
        point = self.player.front_point()
        items = [("Preparo", self.prep.x + self.prep.bench.get_width() // 2, self.prep.y, self.prep.interact)]
        items += [(st.label, st.x + st.surf.get_width() // 2, st.y, st.interact) for st in self.stations]
        prop = self._facing_prop()
        if prop is not None and prop.name == "tool_bench":
            ferramenta_txt = "Mãos Livres" if self.equipped_tool is None else self.equipped_tool.upper()
            items.append((f"Bancada ({ferramenta_txt})", prop.x + 17, prop.y, prop.interact))

        for text, cx, top, rect in items:
            if rect.collidepoint(point):
                continue  
            label = self.label_font.render(text, True, cfg.DLG_TEXT)
            w = label.get_width() + 6
            lh = label.get_height()
            box = pygame.Rect(cx - self.camera.x - w // 2, top - self.camera.y - lh - 2, w, lh + 1)
            if -w < box.x < cfg.NATIVE_WIDTH:
                DialogueBox._draw_frame(surface, box)
                surface.blit(label, (box.x + 3, box.y))

    def _draw_facing_hint(self, surface: pygame.Surface) -> None:
        point = self.player.front_point()
        for plot in self.plots:
            if plot.interact.collidepoint(point):
                self._draw_hint_at(surface, plot.x + 8, plot.y)
                return
        targets = [(self.prep.interact, self.prep.x + 17, self.prep.y)]
        targets += [(st.interact, st.x + st.surf.get_width() // 2, st.y) for st in self.stations]
        prop = self._facing_prop()
        if prop is not None and prop.name == "tool_bench":
            targets.append((prop.interact, prop.x + 17, prop.y))

        for rect, cx, top in targets:
            if rect.collidepoint(point):
                self._draw_hint_at(surface, cx, top)
                return
        if prop is not None:
            r = prop.solid or pygame.Rect(prop.x, prop.y, *prop.surf.get_size())
            self._draw_hint_at(surface, r.centerx, prop.y)

    def _draw_hint_at(self, surface: pygame.Surface, world_cx: int, world_top: int) -> None:
        bx = world_cx - self.camera.x - 5
        by = world_top - self.camera.y - 13
        pygame.draw.rect(surface, cfg.DLG_BG, (bx - 1, by - 1, 11, 11), border_radius=2)
        pygame.draw.rect(surface, cfg.DLG_BORDER, (bx - 1, by - 1, 11, 11), 1, border_radius=2)
        surface.blit(self.hint_font.render("Z", True, cfg.DLG_TEXT), (bx + 1, by - 2))

    def _facing_prop(self) -> Prop | None:
        point = self.player.front_point()
        for p in self.props:
            if p.interact is not None and p.interact.collidepoint(point):
                return p
        return None