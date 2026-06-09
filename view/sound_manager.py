# view/sound_manager.py — звуковые эффекты из .wav-файлов
#
# Ожидаемая структура папки assets/sounds/ рядом с main.py:
#
#   assets/
#     sounds/
#       sfx/
#         pea_shoot.wav      — выстрел горошиной
#         gun_shoot.wav      — очередь пулемёта
#         punch.wav          — удар боксёра
#         zombie_die.wav     — смерть зомби
#         base_hit.wav       — удар по базе
#         plant_place.wav    — постановка растения
#       music/
#         background.wav     — фоновая музыка (также поддерживается .ogg/.mp3)
#
# TODO (твоя очередь):
#   1. Создай папки  assets/sounds/sfx/  и  assets/sounds/music/  рядом с main.py
#   2. Положи туда .wav-файлы с именами, перечисленными выше
#   3. Если файл отсутствует — звук тихо пропускается, игра не падает

import pygame
import os


# Путь до папки со звуками — относительно рабочей директории (там, где main.py)
_SOUNDS_ROOT = os.path.join("assets", "sounds")
_SFX_DIR     = os.path.join(_SOUNDS_ROOT, "sfx")
_MUSIC_DIR   = os.path.join(_SOUNDS_ROOT, "music")

# Имена файлов для каждого звукового события (без расширения)
_SFX_FILES = {
    "pea_shoot":  "pea_shoot.wav",
    "gun_shoot":  "gun_shoot.wav",
    "punch":      "punch.wav",
    "zombie_die": "zombie_die.wav",
    "base_hit":   "base_hit.wav",
    "plant_place": "plant_place.wav",
}

# Фоновая музыка — пробуем несколько форматов по порядку
_MUSIC_FILES = (
    os.path.join(_MUSIC_DIR, "background.wav"),
    os.path.join(_MUSIC_DIR, "background.ogg"),
    os.path.join(_MUSIC_DIR, "background.mp3"),
)


class SoundManager:
    """
    Управляет звуковыми эффектами и музыкой.
    Звуки загружаются из файлов .wav в папке assets/sounds/sfx/.
    """

    def __init__(self, sfx_on=True, music_on=True):
        self.sfx_on   = sfx_on
        self.music_on = music_on
        self.sounds   = {}   # {event_name: pygame.mixer.Sound}
        self._ok      = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            self._load_sounds()
            self._ok = True
        except Exception as ex:
            print(f"[SoundManager] ошибка инициализации: {ex}")

    # ------------------------------------------------------------------
    def _load_sounds(self):
        """
        Загружает все .wav-файлы из _SFX_DIR по словарю _SFX_FILES.
        Отсутствующие файлы тихо пропускаются.
        """
        for event_name, filename in _SFX_FILES.items():
            path = os.path.join(_SFX_DIR, filename)
            if os.path.isfile(path):
                try:
                    self.sounds[event_name] = pygame.mixer.Sound(path)
                    print(f"[SoundManager] загружен: {path}")
                except Exception as ex:
                    print(f"[SoundManager] не удалось загрузить {path}: {ex}")
            else:
                # TODO (твоя очередь): положи файл  {path}  чтобы этот звук работал
                print(f"[SoundManager] файл не найден, звук '{event_name}' отключён: {path}")

    # ------------------------------------------------------------------
    def play(self, name: str):
        """Воспроизводит звук по имени события (ключ из _SFX_FILES)."""
        if not self.sfx_on or not self._ok:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    # ------------------------------------------------------------------
    # Фоновая музыка
    # ------------------------------------------------------------------

    def try_play_music(self):
        if not self.music_on or not self._ok:
            return
        for path in _MUSIC_FILES:
            if os.path.isfile(path):
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(0.38)
                    pygame.mixer.music.play(-1)
                    print(f"[Music] играет: {path}")
                except Exception as ex:
                    print(f"[Music] не удалось загрузить {path}: {ex}")
                return
        # TODO (твоя очередь): положи файл background.wav в  assets/sounds/music/
        print("[Music] музыкальный файл не найден, музыка отключена")

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def set_sfx(self, on: bool):
        self.sfx_on = on

    def set_music(self, on: bool):
        self.music_on = on
        if not on:
            self.stop_music()
        else:
            self.try_play_music()
