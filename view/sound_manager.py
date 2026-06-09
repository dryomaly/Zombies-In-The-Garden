# Класс со звуками игры

import pygame
import os

_SFX_DIR = os.path.join("assets", "sounds", "sfx")
_MUSIC_DIR = os.path.join("assets", "sounds", "music")

_SFX_FILES = {
    "pea_shoot": "pea_shoot.wav",
    "gun_shoot": "gun_shoot.wav",
    "punch": "punch.wav",
    "zombie_die": "zombie_die.wav",
    "base_hit": "base_hit.wav",
    "plant_place": "plant_place.wav",
}

_MUSIC_PATH = os.path.join(_MUSIC_DIR, "background.mp3")


class SoundManager:
    def __init__(self, sfx_on=True, music_on=True):
        self.sfx_on = sfx_on
        self.music_on = music_on
        self.sounds = {}

        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)

        for event_name, filename in _SFX_FILES.items():
            self.sounds[event_name] = pygame.mixer.Sound(
                os.path.join(_SFX_DIR, filename)
            )

    def play(self, name: str):
        if self.sfx_on:
            self.sounds[name].play()

    def try_play_music(self):
        if self.music_on:
            pygame.mixer.music.load(_MUSIC_PATH)
            pygame.mixer.music.set_volume(0.38)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_sfx(self, on: bool):
        self.sfx_on = on

    def set_music(self, on: bool):
        self.music_on = on
        if not on:
            self.stop_music()
        else:
            self.try_play_music()
