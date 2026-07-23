"""Objeto do cenario: um sprite com colisor e/ou area de interacao opcionais."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from .camera import Camera


@dataclass
class Prop:
    name: str
    surf: pygame.Surface
    x: int
    y: int
    solid: pygame.Rect | None = None      # colisor (None = atravessavel)
    interact: pygame.Rect | None = None   # area de interacao (None = nao interage)

    @property
    def sort_y(self) -> int:
        """Profundidade para ordenacao (base do objeto)."""
        if self.solid is not None:
            return self.solid.bottom
        return self.y + self.surf.get_height()

    def draw(self, target: pygame.Surface, camera: Camera) -> None:
        if self.name == "boat":
            bx = self.x - camera.x
            by = self.y - camera.y
            pygame.draw.rect(target, (110, 58, 24), (bx, by, 42, 14), border_radius=4)
            pygame.draw.rect(target, (50, 24, 10), (bx, by, 42, 14), 1, border_radius=4)
            pygame.draw.rect(target, (150, 85, 40), (bx + 6, by + 3, 8, 8))
            pygame.draw.rect(target, (150, 85, 40), (bx + 26, by + 3, 8, 8))
            
            pygame.draw.rect(target, (40, 40, 40), (bx - 2, by + 3, 4, 5))
            pygame.draw.rect(target, (70, 70, 70), (bx - 1, by + 2, 3, 2)) 
            pygame.draw.line(target, (80, 80, 80), (bx - 2, by + 5), (bx - 14, by + 11), 1)
            pygame.draw.rect(target, (30, 30, 30), (bx - 15, by + 10, 2, 3))
            
        elif self.name == "tool_bench":
            bx = self.x - camera.x
            by = self.y - camera.y
            pygame.draw.rect(target, (139, 69, 19), (bx, by, 34, 12), border_radius=2)
            pygame.draw.rect(target, (101, 50, 14), (bx, by, 34, 12), 1, border_radius=2)
            
            tool_no_cesto = None
            try:
                import inspect
                for frame_info in inspect.stack():
                    if 'self' in frame_info.frame.f_locals:
                        obj = frame_info.frame.f_locals['self']
                        if obj.__class__.__name__ == 'OutdoorScene':
                            tool_no_cesto = getattr(obj, 'equipped_tool', None)
                            break
            except:
                pass

            if tool_no_cesto != "semente":
                pygame.draw.circle(target, (90, 50, 20), (bx + 6, by + 5), 2)
            if tool_no_cesto != "enxada":
                pygame.draw.line(target, (130, 90, 60), (bx + 14, by + 7), (bx + 22, by + 3), 1)
                pygame.draw.rect(target, (160, 160, 160), (bx + 21, by + 1, 3, 3))
            if tool_no_cesto != "regador":
                pygame.draw.rect(target, (40, 100, 180), (bx + 28, by + 4, 5, 4), border_radius=1)
                pygame.draw.line(target, (20, 60, 140), (bx + 33, by + 5), (bx + 35, by + 5), 1)
            
        else:
            target.blit(self.surf, (self.x - camera.x, self.y - camera.y))
            
            if "stall" in str(self.surf) or (hasattr(self, "label") and getattr(self, "label") == "Banca"):
                bx = self.x - camera.x
                by = self.y - camera.y
                
                # Mascara de madeira tampando os potes fixos da textura
                pygame.draw.rect(target, (122, 85, 52), (bx + 4, by + 11, 24, 6))
                
                barras_estocadas = 0
                try:
                    import inspect
                    for frame_info in inspect.stack():
                        if 'self' in frame_info.frame.f_locals:
                            obj = frame_info.frame.f_locals['self']
                            if obj.__class__.__name__ == 'OutdoorScene':
                                barras_estocadas = getattr(obj, 'sold', 0)
                                break
                except:
                    pass
                
                if barras_estocadas > 0:
                    for i in range(min(barras_estocadas, 3)):
                        st_x = bx + 4 + (i * 8) 
                        st_y = by + 12
                        pygame.draw.rect(target, (58, 34, 20), (st_x, st_y, 6, 4))
                        pygame.draw.rect(target, (35, 18, 8), (st_x, st_y, 6, 4), 1)