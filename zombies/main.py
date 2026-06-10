# Запуск игры

import pygame
import sys

from settings import SCREEN_W, SCREEN_H, FPS, CAPTION
from model.game import GameModel
from view.renderer import Renderer
from view.ui import (draw_menu, draw_level_select, draw_settings,
                     draw_game_over, draw_win, draw_pause_menu)
from view.sound_manager import SoundManager
from controller.input_handler import InputHandler, is_pause


def main():
    pygame.init()
    pygame.mixer.init(44100, -16, 2, 512)

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()

    renderer      = Renderer()
    input_handler = InputHandler()
    sound_manager = SoundManager()

    state         = "menu"
    current_level = 1
    model         = None
    settings      = {"music": True, "sounds": True, "show_grid": True}

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.1)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if (event.type == pygame.KEYDOWN and is_pause(event)
                    and state == "playing" and model):
                model.toggle_pause()

        if state == "menu":
            result = draw_menu(screen, events)
            if result == "level_select": state = "level_select"
            elif result == "settings":   state = "settings"
            elif result == "quit":       running = False

        elif state == "level_select":
            scores = GameModel.load_scores()
            result = draw_level_select(screen, events, scores)
            if result == "back":
                state = "menu"
            elif result and result.startswith("level_"):
                current_level = int(result.split("_")[1])
                model = GameModel(current_level)
                state = "playing"
                sound_manager.try_play_music()

        elif state == "settings":
            result = draw_settings(screen, events, settings)
            if result == "back":
                state = "menu"
            sound_manager.sfx_on   = settings.get("sounds", True)
            sound_manager.music_on = settings.get("music", True)
            if not sound_manager.music_on:
                sound_manager.stop_music()

        elif state == "playing":
            if model is None:
                state = "menu"
                continue
            if not model.paused:
                input_handler.handle(events, model)
            if not model.paused:
                model.update(dt)
                for snd_name in model.pending_sounds:
                    sound_manager.play(snd_name)
                model.pending_sounds.clear()
            renderer.draw(screen, model)
            if model.paused:
                pause_result = draw_pause_menu(screen, events)
                if pause_result == "resume":
                    model.paused = False
                elif pause_result == "menu":
                    model = None
                    state = "menu"
                    sound_manager.stop_music()
                    continue
            if model.state == "game_over": state = "game_over"
            elif model.state == "win":     state = "win"

        elif state == "game_over":
            if model:
                renderer.draw(screen, model)
            result = draw_game_over(screen, events, model.score if model else 0)
            if result == "retry":
                model = GameModel(current_level)
                state = "playing"
                sound_manager.try_play_music()
            elif result == "menu":
                model = None
                state = "menu"
                sound_manager.stop_music()

        elif state == "win":
            if model:
                renderer.draw(screen, model)
            result = draw_win(screen, events, model.score if model else 0, current_level < 3)
            if result == "next" and current_level < 3:
                current_level += 1
                model = GameModel(current_level)
                state = "playing"
                sound_manager.try_play_music()
            elif result == "menu":
                model = None
                state = "menu"
                sound_manager.stop_music()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
