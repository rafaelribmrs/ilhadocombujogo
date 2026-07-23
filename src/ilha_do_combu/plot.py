"""Gerenciador dos canteiros de areia de plantio e transição para colheita."""

from __future__ import annotations

import pygame
from ilha_do_combu import settings as cfg


class Plot:
    def __init__(self, x: int, y: int, stages: list[pygame.Surface], tree_surf: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.stages = stages      
        self.tree_surf = tree_surf  
        self.stage = 0            # 0: Areia, 1: Arada, 2: Semeada, 3: Regada/Crescendo, 4: Pronta

        self.rect = pygame.Rect(x, y, 24, 24)
        self.interact = self.rect.inflate(12, 12)

        self.growth_timer = 0.0
        self.target_growth = 10.0  

        self.minigame_active = False
        self.selected_fruit_index = 1

    @property
    def sort_y(self) -> int:
        """Garante a ordenação correta de renderização (Y-sorting)."""
        if self.stage < 4:
            # Enquanto for apenas o canteiro rasteiro (chão), renderiza sempre no fundo
            return -99999
        # Quando virar árvore adulta, usa a base do tronco para o Y-sort dinâmico
        return self.rect.bottom

    def update(self, dt: float) -> None:
        # A árvore só cresce ativamente se estiver no estágio 3 (após ser regada)
        if self.stage == 3:
            self.growth_timer += dt
            if self.growth_timer >= self.target_growth:
                self.stage = 4
                self.growth_timer = 0.0

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        px = self.x - camera.x
        py = self.y - camera.y

        if self.stage < 4:
            # Mostra o canteiro ou broto correspondente
            idx = min(self.stage, len(self.stages) - 1)
            surface.blit(self.stages[idx], (px, py))
            
            # Desenha a barra de progresso apenas na fase de crescimento ativo (Rega concluída)
            if self.stage == 3:
                progresso = min(1.0, self.growth_timer / self.target_growth)
                lw = int(24 * progresso)
                pygame.draw.rect(surface, (60, 60, 60), (px, py - 6, 24, 3), border_radius=1)
                pygame.draw.rect(surface, (100, 255, 100), (px, py - 6, lw, 3), border_radius=1)
        else:
            # Árvore adulta permanente renderizada no local correto
            surface.blit(self.tree_surf, (px - 12, py - 32))