"""Cena do Campus da UFPA à beira do Rio Guamá.

Aqui o jogador desembarca na Orla, monta sua banca perto do Mirante do Rio
e vende seus chocolates sustentáveis, coletando dinheiro para investir na ilha.
"""

from __future__ import annotations

import random
import pygame

from .. import settings as cfg
from ..camera import Camera
from ..dialogue import DialogueBox
from ..fonts import game_font
from ..player import Player
from ..prop import Prop
from ..tilemap import TileMap
from .base import Scene


UFPA_MAP = [
    "gaaaaaaaaaaaaaaaaaaaaaag",
    "gaaaaaaaaaaaaaaaaaaaaaag",
    "gaaaaaaaaaaaaaaaaaaaaaag",
    "ggggghijklmnopqrstgggggg",
    "gTTTgggggTTTgggggTTTgggg",
    "gTTTgggggTTTgggggTTTgggg",
    "CCCCCCCCCCCCCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCCCCCCCCCC",
    "wwwwwwwwwwwwwwwwwwwwwwww",
    "wwwwwwwwwwwwwwwwwwwwwwww",
]

UFPA_LEGEND = {
    "g": ("grass", False),
    "T": ("grass_tall", False),
    "C": ("concrete", False),  
    "a": ("ciclovia", False),  
    "w": ("water", True),      
}


class UfpaScene(Scene):
    def __init__(self, game, chocolate_para_vender: int = 3) -> None:
        super().__init__(game)
        self.chocolate_count = chocolate_para_vender
        self.money = getattr(game, "money", 0)

        from .. import art
        tiles = art.build_outdoor_tiles()
        
        if "water" in tiles:
            tiles["w"] = tiles["water"]
            
        if "concrete" not in tiles:
            surf = pygame.Surface((16, 16))
            surf.fill((170, 175, 180))
            tiles["concrete"] = surf

        # Ciclovia vermelha clássica de ponta a ponta
        ciclovia_surf = pygame.Surface((16, 16))
        ciclovia_surf.fill((170, 35, 35))
        tiles["ciclovia"] = ciclovia_surf

        char = art.build_character()
        self.tilemap = TileMap(UFPA_MAP, tiles, UFPA_LEGEND)
        self.camera = Camera(self.tilemap.pixel_w, self.tilemap.pixel_h)

        self.player = Player(48, 96, char)
        self.player.direction = "up"

        self.font = game_font(16)
        self.label_font = game_font(15)
        self.small_font = game_font(13)
        self.dialogue = DialogueBox(self.font)
        
        self.colliders = list(self.tilemap.colliders)

        # Fila vertical subindo no gramado
        self.customers = [
            [160, 56, (141, 85, 36), (40, 30, 20), (50, 120, 200), True, False],    
            [180, 56, (224, 172, 105), (120, 80, 40), (220, 100, 50), False, True], 
            [200, 56, (255, 219, 172), (200, 160, 40), (100, 180, 100), True, False] 
        ]

        self.banca_rect = pygame.Rect(144, 80, 36, 32)
        self.barco_rect = pygame.Rect(30, 104, 54, 24)

        # Lista de frases variadas de agradecimento dos estudantes
        self.frases_clientes = [
            "Estudante: 'Que delícia de chocolate! Adoro apoiar a bioeconomia do Combu!'",
            "Professora: 'Maravilhoso! Vou levar para o departamento para saborear com café.'",
            "Estudante: 'Energia pura para aguentar as aulas de Sinais e Sistemas hoje!'",
            "Calouro: 'Nossa, o sabor do cacau nativo é muito superior ao chocolate comum!'",
            "Pesquisador: 'Sustentável e saboroso! É disso que a Amazônia precisa!'"
        ]

        props_assets = art.build_outdoor_props()
        self.props = []
        
        def add_campus_tree(name, x, y):
            surf = props_assets["cacao_tree" if name == "cacao_tree" else "tree"]
            solid = pygame.Rect(x + 11, y + 30, 10, 8)
            self.props.append(Prop(name, surf, x, y, solid, solid.inflate(10, 10)))
            self.colliders.append(solid)

        # Árvores movidas totalmente para fora da ciclofaixa vermelha superior
        add_campus_tree("tree", 10, -35)
        add_campus_tree("cacao_tree", 110, 48)
        add_campus_tree("tree", 220, -35)
        add_campus_tree("cacao_tree", 310, 48)

        # Puxa os assets de fábrica e aplica a banca idêntica à do quintal
        fa = art.build_factory_props()
        banca_surf = fa["stall"]
        
        banca_solid = pygame.Rect(144, 84, 32, 12)
        self.props.append(Prop("banca_ufpa", banca_surf, 144, 72, solid=banca_solid))
        self.colliders.append(banca_solid)

        pages = [
            "Bem-vindo ao Campus da Universidade Federal do Pará (UFPA)!",
            "Você desembarcou na famosa Orla da UFPA, bem em frente ao Mirante do Rio.",
            "Aproxime-se da BANCA DE VENDAS para atender os clientes um por um!"
        ]
        self.dialogue.open(pages, "Porto da UFPA")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.fade is not None:
            return
        
        if event.key in (pygame.K_z, pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
            if self.dialogue.active:
                self.dialogue.advance()
                return

            player_point = (self.player.x + 8, self.player.y + 8)
            
            if self.banca_rect.collidepoint(player_point):
                self._atender_cliente_individual()
                return
                
            if self.barco_rect.collidepoint(player_point):
                self._voltar_para_combu()
                return

    def _atender_cliente_individual(self) -> None:
        if self.chocolate_count > 0 and len(self.customers) > 0:
            self.chocolate_count -= 1
            self.money += 15
            self.game.money = self.money
            
            self.customers.pop(0)
            
            # CORREÇÃO: Fila anda para a esquerda no eixo X ao invés do eixo Y
            for customer in self.customers:
                customer[0] -= 20 
                
            if self.chocolate_count > 0:
                peles = [(141, 85, 36), (224, 172, 105), (255, 219, 172)]
                cabelos = [(40, 30, 20), (120, 80, 40), (200, 160, 40)]
                camisas = [(50, 120, 200), (220, 100, 50), (100, 180, 100), (90, 40, 150)]
                
                # CORREÇÃO: Novo cliente surge no fim da fila horizontal (X + 20)
                ultimo_x = self.customers[-1][0] if len(self.customers) > 0 else 160
                novo_x = ultimo_x + 20
                
                self.customers.append([
                    novo_x, 56, 
                    random.choice(peles), 
                    random.choice(cabelos), 
                    random.choice(camisas), 
                    random.choice([True, False]), 
                    random.choice([True, False])
                ])
                
            frase_aleatoria = random.choice(self.frases_clientes)
            conversas = [
                frase_aleatoria,
                "Você entregou 1 barra de chocolate artesanal fresquinho!",
                "Faturamento da venda: R$ 15,00!",
                f"Sua banca ainda tem {self.chocolate_count} barras prontas no estoque da UFPA."
            ]
            self.dialogue.open(conversas, "Venda Realizada")
        elif self.chocolate_count == 0:
            self.dialogue.open([
                "--- ESTOQUE DE BARRAS VENDIDO ---",
                "Você vendeu todo o chocolate desta remessa!",
                "Os estudantes adoraram. Entre na canoa na água e volte ao Combu para produzir mais!"
            ], "Banca de Vendas")
        else:
            self.dialogue.open([
                "--- FILA REUNIDA ---",
                "Todos os clientes da fila já foram atendidos!",
                "Excelente trabalho! Seu bolso está cheio de recursos para o quintal."
            ], "Banca de Vendas")

    def _voltar_para_combu(self) -> None:
        pages = [
            "Você sobe a bordo da canoa rabeta ancorada na Orla da UFPA.",
            "Partiu navegar de volta descendo o rio Guamá para a Ilha do Combu!"
        ]
        self.dialogue.open(pages, "Canoa Rabeta")
        
        from .river import RiverScene
        self.warp_to(lambda: RiverScene(self.game, direction="volta"))

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
        
        # Desenha a ciclofaixa de ponta a ponta
        for cx in range(0, self.tilemap.pixel_w, 24):
            pygame.draw.line(surface, (245, 245, 245), (cx - self.camera.x, 24 - self.camera.y), (cx + 12 - self.camera.x, 24 - self.camera.y), 1)
        
        # --- DESENHA OS ESTUDANTES ALINHADOS NA HORIZONTAL ---
        for cx, cy, skin, hair, clothes, is_female, has_cap in self.customers:
            px, py = cx - self.camera.x, cy - self.camera.y
            
            if px < -30 or px > cfg.NATIVE_WIDTH + 30:
                continue

            # Cabeça
            pygame.draw.rect(surface, skin, (px + 4, py - 4, 8, 8), border_radius=1)
            # Pescoço
            pygame.draw.rect(surface, skin, (px + 7, py + 4, 2, 2))
            
            # Cabelo ou Boné
            if is_female:
                pygame.draw.rect(surface, hair, (px + 3, py - 5, 10, 3), border_radius=1)
                pygame.draw.rect(surface, hair, (px + 3, py - 2, 2, 6))
                pygame.draw.rect(surface, hair, (px + 11, py - 2, 2, 6))
            else:
                if has_cap:
                    pygame.draw.rect(surface, (200, 50, 50), (px + 3, py - 6, 10, 3))
                    pygame.draw.rect(surface, (30, 30, 30), (px + 1, py - 4, 12, 1))
                else:
                    pygame.draw.rect(surface, hair, (px + 3, py - 5, 10, 3), border_radius=1)
            
            # Olhos
            pygame.draw.rect(surface, (40, 40, 40), (px + 5, py - 1, 1, 1))
            pygame.draw.rect(surface, (40, 40, 40), (px + 9, py - 1, 1, 1))
            
            # Boca/Sorriso
            cor_boca = (50, 25, 12)
            pygame.draw.rect(surface, cor_boca, (px + 7, py + 2, 2, 1))
            pygame.draw.rect(surface, cor_boca, (px + 6, py + 1, 1, 1))
            pygame.draw.rect(surface, cor_boca, (px + 9, py + 1, 1, 1))

            # Corpo/Camisa
            pygame.draw.rect(surface, clothes, (px + 2, py + 5, 12, 10), border_radius=1)
            
            # Braços e Mãos
            pygame.draw.rect(surface, clothes, (px, py + 5, 2, 5))
            pygame.draw.rect(surface, skin, (px, py + 10, 2, 4))
            pygame.draw.rect(surface, clothes, (px + 14, py + 5, 2, 5))
            pygame.draw.rect(surface, skin, (px + 14, py + 10, 2, 4))
            
            # Pernas e Sapatos
            pant_color = (180, 50, 100) if is_female else (40, 60, 150)
            pygame.draw.rect(surface, pant_color, (px + 3, py + 15, 3, 6))   
            pygame.draw.rect(surface, pant_color, (px + 10, py + 15, 3, 6))  
            
            cor_sapato = (40, 30, 30)
            pygame.draw.rect(surface, cor_sapato, (px + 2, py + 21, 4, 2))  
            pygame.draw.rect(surface, cor_sapato, (px + 10, py + 21, 4, 2)) 

        # Desenha os adereços
        drawables = [(p.sort_y, p) for p in self.props]
        drawables.append((self.player.feet.bottom, self.player))
        for _, obj in sorted(drawables, key=lambda d: d[0]):
            obj.draw(surface, self.camera)
        
        # Canoa boiando na água
        barco_x, barco_y = 36 - self.camera.x, 132 - self.camera.y
        pygame.draw.rect(surface, (110, 58, 24), (barco_x, barco_y, 42, 14), border_radius=4)
        pygame.draw.rect(surface, (50, 24, 10), (barco_x, barco_y, 42, 14), 1, border_radius=4)
        pygame.draw.rect(surface, (150, 85, 40), (barco_x + 6, barco_y + 3, 8, 8))
        pygame.draw.rect(surface, (150, 85, 40), (barco_x + 26, barco_y + 3, 8, 8))
        pygame.draw.rect(surface, (40, 40, 40), (barco_x - 2, barco_y + 3, 4, 5))
        pygame.draw.line(surface, (80, 80, 80), (barco_x - 2, barco_y + 5), (barco_x - 14, barco_y + 11), 1)

        # Rótulos de Proximidade
        if not self.dialogue.active:
            player_point = (self.player.x + 8, self.player.y + 8)
            if self.banca_rect.collidepoint(player_point):
                self._draw_action_hint(surface, "Z: Negociar", 160, 68)
            elif self.barco_rect.collidepoint(player_point):
                self._draw_action_hint(surface, "Z: Voltar para a Ilha", 55, 114)

        # HUD
        hud_x, hud_y = 5, 5
        if not self.dialogue.active:
            pygame.draw.rect(surface, cfg.DLG_BG, (hud_x, hud_y, 105, 32), border_radius=3)
            pygame.draw.rect(surface, cfg.DLG_BORDER, (hud_x, hud_y, 105, 32), 1, border_radius=3)
            
            saldo_txt = f"Carteira: R${self.money}"
            estoque_txt = f"Chocolates: {self.chocolate_count}"
            
            surface.blit(self.small_font.render(saldo_txt, True, (100, 255, 100)), (hud_x + 5, hud_y + 3))
            surface.blit(self.small_font.render(estoque_txt, True, (240, 200, 80)), (hud_x + 5, hud_y + 15))

        self.dialogue.draw(surface)
        self.draw_fade(surface)

    def _draw_action_hint(self, surface: pygame.Surface, text: str, world_x: int, world_y: int) -> None:
        label = self.label_font.render(text, True, cfg.DLG_TEXT)
        w = label.get_width() + 6
        lh = label.get_height()
        box = pygame.Rect(world_x - self.camera.x - w // 2, world_y - self.camera.y, w, lh + 1)
        DialogueBox._draw_frame(surface, box)
        surface.blit(label, (box.x + 3, box.y))