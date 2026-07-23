"""Jogador: movimento nas 4 direcoes, colisao por "caixa dos pes" e animacao."""

from __future__ import annotations

import pygame

from . import settings as cfg

ANIM_FPS = 8.0          # quadros por segundo da caminhada
WALK_SPEED = 72.0       # pixels por segundo


class Player:
    def __init__(self, x: int, y: int, frames: dict[str, list[pygame.Surface]]) -> None:
        self.frames = frames
        self.x = float(x)
        self.y = float(y)
        self.w = 16
        self.h = 16
        self.direction = "down"
        self.moving = False
        self._anim_t = 0.0
        self._anim_i = 0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def feet(self) -> pygame.Rect:
        """Caixa de colisao na base do sprite (so os pes colidem)."""
        r = pygame.Rect(0, 0, 10, 5)
        r.midbottom = (int(self.x) + self.w // 2, int(self.y) + self.h - 1)
        return r

    def front_point(self) -> tuple[int, int]:
        """Ponto um tile a frente, usado para detectar interacoes."""
        cx, cy = self.feet.center
        dx, dy = {
            "down": (0, 1),
            "up": (0, -1),
            "left": (-1, 0),
            "right": (1, 0),
        }[self.direction]
        return cx + dx * cfg.TILE_SIZE, cy + dy * cfg.TILE_SIZE

    def update(self, dt: float, keys, colliders: list[pygame.Rect]) -> None:
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            self.direction = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            self.direction = "right"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            self.direction = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            self.direction = "down"

        self.moving = dx != 0 or dy != 0
        if self.moving:
            self.x += dx * WALK_SPEED * dt
            self._resolve(colliders, dx, 0)
            self.y += dy * WALK_SPEED * dt
            self._resolve(colliders, 0, dy)
            self._anim_t += dt
            if self._anim_t >= 1.0 / ANIM_FPS:
                self._anim_t -= 1.0 / ANIM_FPS
                self._anim_i = (self._anim_i + 1) % 4
        else:
            self._anim_i = 0
            self._anim_t = 0.0

    def _resolve(self, colliders: list[pygame.Rect], dx: int, dy: int) -> None:
        feet = self.feet
        for c in colliders:
            if not feet.colliderect(c):
                continue
            if dx > 0:
                feet.right = c.left
            elif dx < 0:
                feet.left = c.right
            if dy > 0:
                feet.bottom = c.top
            elif dy < 0:
                feet.top = c.bottom
            # Reposiciona o jogador a partir da caixa dos pes corrigida.
            self.x = feet.centerx - self.w / 2
            self.y = feet.bottom - (self.h - 1)
            feet = self.feet

    def draw(self, target: pygame.Surface, camera) -> None:
        frame = self.frames[self.direction][self._anim_i if self.moving else 0]
        # Sprites mais altos que o tile sobem, mantendo os pes na base logica.
        offset = frame.get_height() - self.h
        
        bx = int(self.x) - camera.x
        by = int(self.y) - camera.y - offset
        
        target.blit(frame, (bx, by))
        
        # SE ESTIVER OLHANDO PARA FRENTE: Desenha o sorriso 2 pixels mais alto
        if self.direction == "down":
            cor_boca = (50, 25, 12)
            # Diminuímos o valor somado a 'by' para fazer a boca subir em direção aos olhos
            pygame.draw.rect(target, cor_boca, (bx + 6, by + 8, 4, 1))  # Linha central
            pygame.draw.rect(target, cor_boca, (bx + 5, by + 7, 1, 1))  # Canto esquerdo
            pygame.draw.rect(target, cor_boca, (bx + 10, by + 7, 1, 1)) # Canto direito