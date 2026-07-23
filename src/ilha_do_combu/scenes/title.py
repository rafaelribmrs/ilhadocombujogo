"""Cena da tela de título dinâmica com rio animado, canoa e menu de seleção."""

from __future__ import annotations

import math
import pygame

from .. import settings as cfg
from ..fonts import game_font
from .base import Scene
from .house import HouseScene
from .outdoor import OutdoorScene


class TitleScene(Scene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.font_title = game_font(20)
        self.font_menu = game_font(13)
        self.font_footer = game_font(11)
        
        self.menu_index = 0
        self.has_save = self.game.save_exists()

        # Variáveis de animação do ambiente nativo
        self.water_scroll = 0.0
        self.anim_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.fade is not None:
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            if self.has_save:
                self.menu_index = 0
                
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            if self.has_save:
                self.menu_index = 1

        elif event.key in (pygame.K_z, pygame.K_SPACE, pygame.K_RETURN):
            if self.menu_index == 0:
                self.game.money = 0
                self.game.saved_bars = 0
                self.game.harvested_seeds = 0
                self.warp_to(lambda: HouseScene(self.game, entry="default"))
            elif self.menu_index == 1 and self.has_save:
                if self.game.load_game():
                    self.warp_to(lambda: OutdoorScene(self.game, entry="from_boat"))

    def update(self, dt: float) -> None:
        self.update_fade(dt)
        
        # Movimentação das ondas e timer de flutuação
        self.anim_timer += dt * 4.0
        self.water_scroll += 30.0 * dt
        if self.water_scroll >= 32.0:
            self.water_scroll = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        # 3. TELA INICIAL BONITA E DINÂMICA: Fundo de rio animado
        surface.fill((70, 130, 196)) # Cor d'água padrão do rio

        # Desenha correntes d'água se movendo lateralmente
        for y in range(0, cfg.NATIVE_HEIGHT, 16):
            scroll_x = (y * 2 + int(self.water_scroll)) % 48
            pygame.draw.line(surface, (100, 160, 220), (scroll_x - 30, y + 8), (scroll_x + 10, y + 8), 1)
            pygame.draw.line(surface, (100, 160, 220), (scroll_x + 100, y + 4), (scroll_x + 130, y + 4), 1)

        # Margem superior verde floresta
        pygame.draw.rect(surface, (34, 110, 45), (0, 0, cfg.NATIVE_WIDTH, 24))
        # Margem inferior verde floresta
        pygame.draw.rect(surface, (34, 110, 45), (0, cfg.NATIVE_HEIGHT - 24, cfg.NATIVE_WIDTH, 24))

        # Desenha mini-árvores nativas na grama das margens
        for mx in range(10, cfg.NATIVE_WIDTH, 64):
            pygame.draw.circle(surface, (20, 80, 30), (mx, 10), 8)
            pygame.draw.circle(surface, (20, 80, 30), (mx + 20, cfg.NATIVE_HEIGHT - 12), 8)

        # Desenha uma canoa flutuando suavemente pelo rio com efeito Seno
        boat_offset_y = int(math.sin(self.anim_timer) * 3)
        bx, by = 24, 75 + boat_offset_y
        pygame.draw.rect(surface, (110, 58, 24), (bx, by, 42, 14), border_radius=4)
        pygame.draw.rect(surface, (150, 85, 40), (bx + 8, by + 3, 8, 8))
        pygame.draw.rect(surface, (150, 85, 40), (bx + 26, by + 3, 8, 8))

        # Faixa escura estilizada central para o menu de texto
        pygame.draw.rect(surface, (15, 30, 20, 220), (84, 25, 142, 112), border_radius=4)
        pygame.draw.rect(surface, (240, 200, 80), (84, 25, 142, 112), 1, border_radius=4)

        # Título do Jogo
        txt_title = self.font_title.render("COMBÚ", True, (255, 255, 255))
        txt_sub = self.font_footer.render("A Semente do Cacau", True, (240, 200, 80))
        surface.blit(txt_title, (155 - txt_title.get_width() // 2, 32))
        surface.blit(txt_sub, (155 - txt_sub.get_width() // 2, 54))

        # Opções do Menu
        color_new = (240, 200, 80) if self.menu_index == 0 else (255, 255, 255)
        txt_new = self.font_menu.render("Novo Jogo", True, color_new)
        
        if self.has_save:
            color_load = (240, 200, 80) if self.menu_index == 1 else (255, 255, 255)
            txt_load = self.font_menu.render("Carregar Jogo", True, color_load)
        else:
            txt_load = self.font_menu.render("Sem Progresso", True, (90, 110, 95))

        seta = self.font_menu.render(">", True, (240, 200, 80))

        # Novo Jogo
        ny = 80
        surface.blit(txt_new, (155 - txt_new.get_width() // 2, ny))
        if self.menu_index == 0:
            surface.blit(seta, (145 - txt_new.get_width() // 2 - 4, ny))

        # Carregar Jogo
        ly = 102
        surface.blit(txt_load, (155 - txt_load.get_width() // 2, ly))
        if self.menu_index == 1 and self.has_save:
            surface.blit(seta, (145 - txt_load.get_width() // 2 - 4, ly))

        # Instruções de controle básicas
        txt_footer = self.font_footer.render("Setas / Z para entrar", True, (140, 160, 145))
        surface.blit(txt_footer, (155 - txt_footer.get_width() // 2, 124))

        self.draw_fade(surface)