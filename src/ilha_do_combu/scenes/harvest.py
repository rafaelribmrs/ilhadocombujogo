"""Cena frontal interativa e aquecida para colheita dos frutos de cacau usando o mouse."""

from __future__ import annotations

import math
import pygame
from ilha_do_combu import settings as cfg
from ilha_do_combu.dialogue import DialogueBox
from ilha_do_combu.fonts import game_font
from .base import Scene


class HarvestScene(Scene):
    def __init__(self, game, parent_plot: "Plot") -> None:
        super().__init__(game)
        self.parent_plot = parent_plot
        self.font = game_font(16)
        self.small_font = game_font(13)
        self.dialogue = DialogueBox(self.font)

        from ilha_do_combu import art
        self.char_sprite = art.build_character()["right"][0]

        # 3. CENÁRIO QUENTE E AMBIENTADO: 7 frutos variados espalhados pela copa vistos de frente
        # [Rect, tipo, cor, texto]
        self.fruits = [
            [pygame.Rect(90, 25, 8, 12), "verde", (120, 175, 40), "Este cacau está verde. Precisamos esperar um tempo..."],
            [pygame.Rect(102, 45, 10, 15), "maduro", (245, 190, 30), "Este cacau está perfeito, use-o! Sementes coletadas."],
            [pygame.Rect(120, 20, 9, 13), "verde", (110, 165, 35), "Este cacau está verde. Precisamos esperar um tempo..."],
            [pygame.Rect(132, 52, 11, 16), "maduro", (240, 185, 25), "Este cacau está perfeito, use-o! Sementes coletadas."],
            [pygame.Rect(148, 28, 9, 14), "passado", (145, 85, 35), "Este cacau está passado do ponto. Pode azedar a fermentação!"],
            [pygame.Rect(155, 46, 10, 15), "maduro", (245, 190, 30), "Este cacau está perfeito, use-o! Sementes coletadas."],
            [pygame.Rect(114, 34, 9, 14), "passado", (135, 75, 30), "Este cacau está passado do ponto. Pode azedar a fermentação!"]
        ]
        
        self.hover_index = -1
        self.finished = False
        self.cloud_scroll = 0.0

        self.dialogue.open([
            "--- VISÃO DA COLHEITA AGROFLORESTAL ---",
            "Mova o mouse sobre a copa para avaliar a maturação de cada fruto.",
            "Dica: Selecione e clique nos frutos amarelos e bem maduros!"
        ], "Colheita Tática")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.fade is not None:
            return

        if self.dialogue.active:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_z, pygame.K_SPACE, pygame.K_RETURN):
                self.dialogue.advance()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            win_w, win_h = pygame.display.get_surface().get_size()
            rx = int(mx * (cfg.NATIVE_WIDTH / win_w))
            ry = int(my * (cfg.NATIVE_HEIGHT / win_h))

            for i, (rect, tipo, _, texto) in enumerate(self.fruits):
                if rect.collidepoint((rx, ry)):
                    if tipo == "maduro":
                        from ilha_do_combu.scenes.outdoor import OutdoorScene
                        self.dialogue.open([texto, "Excelente escolha! As amêndoas nativas foram adicionadas ao seu estoque."], "Sucesso")
                        self.finished = True
                        
                        # 4. MANTÉM A ÁRVORE DISPONÍVEL: Agora o estágio continua em 4 (A árvore não some!)
                        self.parent_plot.stage = 4  
                        return
                    else:
                        self.dialogue.open([texto, "Examine os outros frutos pendurados para colher."], "Aviso")
                        return

    def update(self, dt: float) -> None:
        if self.update_fade(dt):
            return
        if self.dialogue.active:
            self.dialogue.update(dt)
            return

        # Movimentação das nuvens ao fundo do cenário
        self.cloud_scroll += 4.0 * dt
        if self.cloud_scroll >= cfg.NATIVE_WIDTH:
            self.cloud_scroll = 0.0

        if self.finished and not self.dialogue.active:
            from ilha_do_combu.scenes.outdoor import OutdoorScene
            # 4. RETORNO AO LADO DA ÁRVORE: Passamos a coordenada x e y exatas da árvore colhida para o ponto de spawn
            scene_outdoor = OutdoorScene(self.game, entry="from_harvest")
            scene_outdoor.player.x = self.parent_plot.x - 16
            scene_outdoor.player.y = self.parent_plot.y + 12
            scene_outdoor.player.direction = "up"
            
            scene_outdoor.harvested += 1
            scene_outdoor.game.harvested_seeds = scene_outdoor.harvested
            scene_outdoor.has_basket = True
            self.warp_to(lambda: scene_outdoor)
            return

        mx, my = pygame.mouse.get_pos()
        win_w, win_h = pygame.display.get_surface().get_size()
        rx = int(mx * (cfg.NATIVE_WIDTH / win_w))
        ry = int(my * (cfg.NATIVE_HEIGHT / win_h))

        self.hover_index = -1
        for i, (rect, _, _, _) in enumerate(self.fruits):
            if rect.collidepoint((rx, ry)):
                self.hover_index = i

    def draw(self, surface: pygame.Surface) -> None:
        # Céu quente amazônico do Combu
        surface.fill((135, 206, 235))

        # --- 3. NUVENS E DETALHES DE FUNDO ANIMADOS ---
        cx = int(self.cloud_scroll)
        pygame.draw.circle(surface, (255, 255, 255, 200), (cx - 40, 20), 12)
        pygame.draw.circle(surface, (255, 255, 255, 200), (cx - 25, 18), 16)
        pygame.draw.circle(surface, (255, 255, 255, 200), (cx - 10, 20), 12)
        
        pygame.draw.circle(surface, (255, 255, 255, 200), (cx + 140, 25), 10)
        pygame.draw.circle(surface, (255, 255, 255, 200), (cx + 155, 22), 14)

        # Montanhas e matas ciliares distantes no horizonte
        pygame.draw.polygon(surface, (25, 85, 40), [(0, 80), (60, 60), (140, 80)])
        pygame.draw.polygon(surface, (20, 75, 35), [(100, 80), (180, 55), (240, 80)])

        # Solo/Grama de frente
        pygame.draw.rect(surface, (34, 139, 34), (0, 80, cfg.NATIVE_WIDTH, 80))

        # Árvore grande detalhada com sombreado retro
        pygame.draw.rect(surface, (101, 50, 14), (112, 60, 16, 42)) 
        pygame.draw.circle(surface, (46, 125, 50), (125, 40), 40)
        pygame.draw.circle(surface, (27, 94, 32), (105, 35), 25)

        # Frutos pendurados
        for i, (rect, _, cor, _) in enumerate(self.fruits):
            pygame.draw.ellipse(surface, cor, rect)
            pygame.draw.ellipse(surface, (40, 40, 40), rect, 1) # Pixel-outline
            
            # Pequenos pontos de brilho retro nos cacaus para dar textura realista
            pygame.draw.rect(surface, (255, 255, 255), (rect.x + 3, rect.y + 3, 1, 2))

            if i == self.hover_index:
                pygame.draw.rect(surface, (255, 255, 255), rect.inflate(4, 4), 1, border_radius=1)

        # Personagem ao lado esquerdo olhando de lado
        surface.blit(self.char_sprite, (55, 75))

        if not self.dialogue.active:
            pygame.draw.rect(surface, cfg.DLG_BG, (5, 5, 80, 16), border_radius=2)
            surface.blit(self.small_font.render("Use o Mouse", True, cfg.DLG_TEXT), (9, 7))

        self.dialogue.draw(surface)
        self.draw_fade(surface)