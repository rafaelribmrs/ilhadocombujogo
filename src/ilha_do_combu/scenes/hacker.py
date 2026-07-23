"""Módulo Hacker / Ferramenta de Debug para testes rápidos.

Permite alterar o estoque da banca, dinheiro do jogador e teletransportar
diretamente entre os cenários do jogo usando o teclado.
"""

from __future__ import annotations

import pygame

from .. import settings as cfg
from ..fonts import game_font


class HackerMenu:
    def __init__(self) -> None:
        self.active = False
        self.font = game_font(13)
        self.input_text = ""
        self.target_mode = "banca"  # "banca", "carteira" ou "cenário"

    def handle_event(self, event: pygame.event.Event, current_scene) -> None:
        # Pressione 'H' para abrir/fechar o painel hacker
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            self.active = not self.active
            self.input_text = ""
            return

        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            # TAB rotaciona entre os modos de alteração
            if event.key == pygame.K_TAB:
                if self.target_mode == "banca":
                    self.target_mode = "carteira"
                elif self.target_mode == "carteira":
                    self.target_mode = "cenário"
                else:
                    self.target_mode = "banca"
                self.input_text = ""
            
            # Confirma a ação ao pressionar ENTER
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.input_text.isdigit():
                    valor = int(self.input_text)
                    
                    if self.target_mode == "banca":
                        if hasattr(current_scene, "sold"):
                            current_scene.sold = valor
                        if hasattr(current_scene, "chocolate_count"):
                            current_scene.chocolate_count = valor
                            
                    elif self.target_mode == "carteira":
                        current_scene.game.money = valor
                        if hasattr(current_scene, "money"):
                            current_scene.money = valor
                            
                    elif self.target_mode == "cenário":
                        # --- MOTOR DE TELETRANSPORTE DIRETO VIA HACK ---
                        if valor == 1:
                            from ilha_do_combu.scenes.house import HouseScene
                            current_scene.warp_to(lambda: HouseScene(current_scene.game, entry="default"))
                        elif valor == 2:
                            from ilha_do_combu.scenes.outdoor import OutdoorScene
                            current_scene.warp_to(lambda: OutdoorScene(current_scene.game, entry="from_house"))
                        elif valor == 3:
                            from ilha_do_combu.scenes.river import RiverScene
                            current_scene.warp_to(lambda: RiverScene(current_scene.game, direction="ida"))
                        elif valor == 4:
                            from ilha_do_combu.scenes.ufpa import UfpaScene
                            current_scene.warp_to(lambda: UfpaScene(current_scene.game, chocolate_para_vender=3))

                self.active = False
                self.input_text = ""
            
            # Apagar caracteres
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            
            # Captura dígitos numéricos
            elif event.unicode.isdigit():
                self.input_text += event.unicode

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        box_w, box_h = 175, 58
        box_x = (cfg.NATIVE_WIDTH - box_w) // 2
        box_y = 5

        # Painel Visual Retro Vermelho
        pygame.draw.rect(surface, (20, 20, 20), (box_x, box_y, box_w, box_h), border_radius=3)
        pygame.draw.rect(surface, (255, 50, 50), (box_x, box_y, box_w, box_h), 1, border_radius=3)

        # Textos informativos de ajuda dinâmicos
        modo_txt = f"Modo: {self.target_mode.upper()} (TAB)"
        
        if self.target_mode == "cenário":
            val_txt = f"Cenário (1-4): {self.input_text}_"
            ajuda_txt = "1:Casa 2:Quintal 3:Rio 4:UFPA"
        else:
            val_txt = f"Digite o Valor: {self.input_text}_"
            ajuda_txt = "Pressione ENTER para aplicar"
        
        surface.blit(self.font.render(modo_txt, True, (255, 80, 80)), (box_x + 6, box_y + 4))
        surface.blit(self.font.render(val_txt, True, (255, 255, 255)), (box_x + 6, box_y + 20))
        surface.blit(self.font.render(ajuda_txt, True, (140, 140, 140)), (box_x + 6, box_y + 38))