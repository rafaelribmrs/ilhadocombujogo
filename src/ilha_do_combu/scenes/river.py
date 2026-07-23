"""Cena do mini-game de travessia do Rio Guama.

Suporta duas direções: IDA (subindo para a UFPA) e VOLTA (descendo para o Combu).
O jogador desvia de troncos e coleta lixo plástico.
"""

from __future__ import annotations

import random
import pygame

from .. import settings as cfg
from ..dialogue import DialogueBox
from ..fonts import game_font
from .base import Scene


class RiverScene(Scene):
    def __init__(self, game, retry: bool = False, direction: str = "ida", bars_to_save: int = 0) -> None:
        super().__init__(game)
        self.direction = direction  # "ida" ou "volta"
        self.bars_to_save = bars_to_save  # Guarda as barras que sobram caso bata na volta
        self.font = game_font(16)
        self.small_font = game_font(13)
        self.dialogue = DialogueBox(self.font)

        from .. import art
        sprites = art.build_character()
        
        # Ajusta a orientação do herói dependendo do rumo da viagem
        if self.direction == "ida":
            self.char_sprite = sprites["up"][0]  # Piloto de costas
            self.boat_y = cfg.NATIVE_HEIGHT - 60
        else:
            self.char_sprite = sprites["down"][0]  # Piloto de frente
            self.boat_y = 20

        # Estado da canoa
        self.boat_x = cfg.NATIVE_WIDTH // 2 - 7
        self.boat_speed = 120.0  
        self.health = 3          
        self.plastic_collected = 0
        self.distance_traveled = 0.0
        self.target_distance = 300.0  

        self.obstacles = []
        self.spawn_timer = 0.0
        self.water_scroll = 0.0

        if retry:
            self.dialogue.open(["Tente novamente! Controle a canoa com cuidado!"], "Canoa Rabeta")
        else:
            if self.direction == "ida":
                pages = [
                    "Ligando o motor de popa... Esta é a nossa famosa CANOA RABETA!",
                    "O Rio Guamá conecta a Ilha do Combu à UFPA, mas sofre muito com o lixo plástico.",
                    "DESAFIO ECOLÓGICO:\nUse as SETAS [Esquerda/Direita] para guiar o barco.\n\nEvite os TRONCOS, mas RECOLHA as GARRAFAS PLÁSTICAS!"
                ]
            else:
                pages = [
                    "Saindo da UFPA de volta para a Ilha do Combu!",
                    "A maré e o vento estão a nosso favor na descida do rio Guamá.",
                    "Mantenha a atenção para desviar dos obstáculos no caminho de volta!"
                ]
            self.dialogue.open(pages, "Canoa Rabeta")
            
        self.game_started = False
        self.finished = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.fade is not None:
            return
        
        if event.key in (pygame.K_z, pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
            if self.dialogue.active:
                self.dialogue.advance()
                if not self.dialogue.active and not self.game_started and not self.finished:
                    self.game_started = True

    def update(self, dt: float) -> None:
        if self.update_fade(dt):
            return

        if self.dialogue.active:
            self.dialogue.update(dt)
            return

        if not self.game_started or self.finished:
            return

        scroll_dir = 1.0 if self.direction == "ida" else -1.0
        self.water_scroll += 60.0 * dt * scroll_dir
        if abs(self.water_scroll) >= 16:
            self.water_scroll = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.boat_x -= self.boat_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.boat_x += self.boat_speed * dt

        self.boat_x = max(20, min(self.boat_x, cfg.NATIVE_WIDTH - 35))

        self.distance_traveled += 15.0 * dt
        if self.distance_traveled >= self.target_distance:
            self._trigger_finish()
            return

        if self.distance_traveled < self.target_distance - 60.0:
            self.spawn_timer += dt
            if self.spawn_timer >= 1.2:
                self.spawn_timer = 0.0
                x_pos = random.randint(25, cfg.NATIVE_WIDTH - 45)
                tipo = random.choice(["tronco", "plastico"])
                vel = random.randint(70, 110)
                
                if self.direction == "ida":
                    self.obstacles.append([x_pos, -20.0, tipo, vel])
                else:
                    self.obstacles.append([x_pos, cfg.NATIVE_HEIGHT + 10, tipo, -vel])

        player_rect = pygame.Rect(self.boat_x, self.boat_y, 14, 42)
        for item in self.obstacles[:]:
            item[1] += item[3] * dt  
            
            if self.direction == "ida" and item[1] > cfg.NATIVE_HEIGHT:
                self.obstacles.remove(item)
                continue
            elif self.direction == "volta" and item[1] < -30:
                self.obstacles.remove(item)
                continue

            item_rect = pygame.Rect(item[0], item[1], 12, 12)
            if player_rect.colliderect(item_rect):
                if item[2] == "tronco":
                    self.health -= 1
                    self.obstacles.remove(item)
                    if self.health <= 0:
                        self._trigger_fail()
                elif item[2] == "plastico":
                    self.plastic_collected += 1
                    self.obstacles.remove(item)

    def _trigger_finish(self) -> None:
        self.finished = True
        self.game_started = False
        
        if self.direction == "ida":
            pages = [
                "Terra firme à vista! Você ancorou com sucesso no Porto da UFPA!",
                f"Excelente! Você coletou {self.plastic_collected} garrafas plásticas flutuantes que poluiriam o rio.",
                "Pressione Z para desembarcar na universidade."
            ]
            self.dialogue.open(pages, "UFPA Alcançada!")
        else:
            pages = [
                "Você retornou à Ilha do Combu com segurança!",
                f"Você retirou mais {self.plastic_collected} garrafas de lixo do rio no caminho de volta.",
                "Pressione Z para voltar a trabalhar na sua agrofloresta."
            ]
            self.dialogue.open(pages, "Retorno ao Combu")

    def _trigger_fail(self) -> None:
        self.finished = True
        self.game_started = False
        self.dialogue.open(["A canoa sofreu muitos danos!", "Pressione Z para reiniciar este trecho da travessia."], "Casco Quebrado")

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((70, 130, 196))

        for y in range(-16, cfg.NATIVE_HEIGHT + 16, 32):
            scroll_y = y + int(self.water_scroll)
            pygame.draw.line(surface, (100, 160, 220), (10, scroll_y), (40, scroll_y), 1)
            pygame.draw.line(surface, (100, 160, 220), (cfg.NATIVE_WIDTH - 50, scroll_y + 16), (cfg.NATIVE_WIDTH - 20, scroll_y + 16), 1)

        pygame.draw.rect(surface, (34, 110, 45), (0, 0, 15, cfg.NATIVE_HEIGHT))
        pygame.draw.rect(surface, (34, 110, 45), (cfg.NATIVE_WIDTH - 15, 0, 15, cfg.NATIVE_HEIGHT))

        if self.distance_traveled >= self.target_distance - 60.0:
            progresso_chegada = (self.distance_traveled - (self.target_distance - 60.0)) / 60.0
            margem_h = int(progresso_chegada * 40)
            if self.direction == "ida":
                pygame.draw.rect(surface, (170, 175, 180), (0, 0, cfg.NATIVE_WIDTH, margem_h))
                if margem_h > 2:
                    pygame.draw.line(surface, (50, 50, 50), (0, margem_h), (cfg.NATIVE_WIDTH, margem_h), 2)
            else:
                pygame.draw.rect(surface, (34, 110, 45), (0, cfg.NATIVE_HEIGHT - margem_h, cfg.NATIVE_WIDTH, margem_h))
                if margem_h > 2:
                    pygame.draw.line(surface, (20, 60, 20), (0, cfg.NATIVE_HEIGHT - margem_h), (cfg.NATIVE_WIDTH, cfg.NATIVE_HEIGHT - margem_h), 2)

        for item in self.obstacles:
            ix, iy, tipo = int(item[0]), int(item[1]), item[2]
            if tipo == "tronco":
                pygame.draw.rect(surface, (101, 50, 14), (ix, iy, 14, 6), border_radius=1)
            elif tipo == "plastico":
                pygame.draw.rect(surface, (30, 144, 255), (ix + 1, iy + 2, 6, 8), border_radius=1)
                pygame.draw.rect(surface, (240, 240, 240), (ix + 3, iy, 2, 2))

        bx, by = int(self.boat_x), int(self.boat_y)
        pygame.draw.rect(surface, (110, 58, 24), (bx, by, 14, 42), border_radius=4)
        pygame.draw.rect(surface, (50, 24, 10), (bx, by, 14, 42), 1, border_radius=4)
        pygame.draw.rect(surface, (150, 85, 40), (bx + 3, by + 10, 8, 8))
        pygame.draw.rect(surface, (150, 85, 40), (bx + 3, by + 28, 8, 8))
        
        if self.direction == "ida":
            surface.blit(self.char_sprite, (bx - 1, by + 16))
            pygame.draw.rect(surface, (40, 40, 40), (bx + 5, by + 42, 4, 4))
            pygame.draw.line(surface, (80, 80, 80), (bx + 7, by + 44), (bx + 7, by + 54), 1)
        else:
            cx, cy = bx - 1, by + 10
            surface.blit(self.char_sprite, (cx, cy))
            
            # CORREÇÃO: Desenha o sorriso procedural na face quando estiver olhando para frente (volta)
            cor_boca = (50, 25, 12)
            pygame.draw.rect(surface, cor_boca, (cx + 6, cy + 8, 4, 1))  # Linha central
            pygame.draw.rect(surface, cor_boca, (cx + 5, cy + 7, 1, 1))  # Canto esquerdo
            pygame.draw.rect(surface, cor_boca, (cx + 10, cy + 7, 1, 1)) # Canto direito
            
            pygame.draw.rect(surface, (40, 40, 40), (bx + 5, by - 4, 4, 4))
            pygame.draw.line(surface, (80, 80, 80), (bx + 7, by - 4), (bx + 7, by - 14), 1)

        if self.game_started:
            surface.blit(self.small_font.render(f"Casco: {self.health}/3", True, (255, 100, 100)), (20, 5))
            surface.blit(self.small_font.render(f"Lixo Recolhido: {self.plastic_collected}", True, (100, 255, 100)), (20, 18))
            barra_w = 60
            progresso = min(1.0, self.distance_traveled / self.target_distance)
            pygame.draw.rect(surface, (80, 80, 80), (cfg.NATIVE_WIDTH - 80, 8, barra_w, 6), border_radius=2)
            pygame.draw.rect(surface, (100, 255, 100), (cfg.NATIVE_WIDTH - 80, 8, int(barra_w * progresso), 6), border_radius=2)

        self.dialogue.draw(surface)
        self.draw_fade(surface)

        if self.finished and not self.dialogue.active:
            if self.health <= 0:
                self.warp_to(lambda: RiverScene(self.game, retry=True, direction=self.direction, bars_to_save=self.bars_to_save))
            else:
                if self.direction == "ida":
                    from .ufpa import UfpaScene
                    self.warp_to(lambda: UfpaScene(self.game, chocolate_para_vender=self.bars_to_save))
                else:
                    from .outdoor import OutdoorScene
                    self.warp_to(lambda: OutdoorScene(self.game, entry="from_boat"))