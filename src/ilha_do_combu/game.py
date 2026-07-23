"""Loop principal e gerenciador de cenas e progresso (Save/Load)."""

from __future__ import annotations

import json
import os

import pygame

from . import settings as cfg
from .scenes.hacker import HackerMenu


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(f"{cfg.TITLE} - {cfg.SUBTITLE}")
        self.screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
        self.native = pygame.Surface((cfg.NATIVE_WIDTH, cfg.NATIVE_HEIGHT)).convert()
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene: "object | None" = None
        
        # Atributos de progresso persistente do jogador
        self.money = 0
        self.saved_bars = 0
        self.harvested_seeds = 0

        self.hacker = HackerMenu()
        self._smoke_frames = int(os.environ.get("ICOMBU_SMOKE_FRAMES", "0"))

    def change_scene(self, scene) -> None:
        self.scene = scene

    def quit(self) -> None:
        self.running = False

    # --- SISTEMA DE SALVAMENTO AUTOMÁTICO (JSON) ---
    def save_exists(self) -> bool:
        """Verifica se há um arquivo de save criado."""
        return os.path.exists("savegame.json")

    def save_game(self) -> None:
        """Salva as informações de carteira, banca e colheita."""
        data = {
            "money": self.money,
            "saved_bars": self.saved_bars,
            "harvested_seeds": self.harvested_seeds
        }
        try:
            with open("savegame.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar o jogo: {e}")

    def load_game(self) -> bool:
        """Carrega as variáveis salvas para o motor do jogo."""
        if not self.save_exists():
            return False
        try:
            with open("savegame.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.money = data.get("money", 0)
                self.saved_bars = data.get("saved_bars", 0)
                self.harvested_seeds = data.get("harvested_seeds", 0)
            return True
        except Exception as e:
            print(f"Erro ao carregar o jogo: {e}")
            return False

    def run(self) -> None:
        frame = 0
        while self.running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.scene is not None:
                    self.hacker.handle_event(event, self.scene)
                    if not self.hacker.active:
                        self.scene.handle_event(event)

            if self.scene is not None:
                if not self.hacker.active:
                    self.scene.update(dt)
                self.scene.draw(self.native)
            else:
                self.native.fill(cfg.BLACK)

            self.hacker.draw(self.native)

            pygame.transform.scale(self.native, self.screen.get_size(), self.screen)
            pygame.display.flip()

            frame += 1
            if self._smoke_frames and frame >= self._smoke_frames:
                self.running = False

        pygame.quit()