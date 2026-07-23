"""Ponto de entrada principal para rodar o jogo Ilha do Combu."""

from __future__ import annotations

import os
import sys
import pygame

# Ajuste dinâmico de caminho para garantir que as importações funcionem sem erros de pacotes
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ilha_do_combu import settings as cfg
from ilha_do_combu.game import Game
from ilha_do_combu.scenes.title import TitleScene # CONFIGURADO: Inicia diretamente no menu principal
from ilha_do_combu.scenes.hacker import HackerMenu  


def main() -> int:
    pygame.init()
    pygame.display.set_caption("Ilha do Combu - A Semente do Cacau")
    
    # Cria a janela principal do Windows
    screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.NATIVE_HEIGHT * (cfg.WINDOW_WIDTH // cfg.NATIVE_WIDTH)))
    game = Game()
    clock = pygame.time.Clock()
    
    # Inicializa o jogo na Tela de Título com opções de Novo/Carregar Jogo
    game.change_scene(TitleScene(game))
    
    hacker = HackerMenu()

    running = True
    while running:
        dt = clock.tick(cfg.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game.scene is not None:
                hacker.handle_event(event, game.scene)
            
            if not hacker.active and game.scene is not None:
                game.scene.handle_event(event)

        if not hacker.active and game.scene is not None:
            game.scene.update(dt)

        if game.scene is not None:
            game.native.fill(cfg.BLACK)
            game.scene.draw(game.native)

        hacker.draw(game.native)

        scaled = pygame.transform.scale(game.native, screen.get_size())
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())