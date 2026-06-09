# view/sound_manager.py — звуковые эффекты, генерируются программно
#
# Не требует внешних аудио-файлов: все звуки создаются математически
# через синусоиды и огибающие. Если нужна музыка — положи файл
# sounds/music.ogg (или .mp3 / .wav) рядом с main.py.

import pygame
import math
import array
import os


def _gen(freq, ms, vol=0.35, wave='sine', rate=44100):
    """
    Генерирует стерео 16-bit звук заданной частоты и длительности.
    wave: 'sine' | 'square' | 'descend'
    """
    n = int(rate * ms / 1000)
    data = []
    for i in range(n):
        t = i / rate
        progress = i / n if n > 0 else 0

        # Огибающая: быстрая атака, линейное затухание
        attack  = min(1.0, t * 80)
        sustain = max(0.0, 1.0 - progress * 1.3)
        env = attack * sustain

        if wave == 'square':
            raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == 'descend':
            f = freq * (1.0 - progress * 0.6)   # частота падает
            raw = math.sin(2 * math.pi * f * t)
        else:
            raw = math.sin(2 * math.pi * freq * t)

        v = int(raw * env * vol * 32767)
        v = max(-32768, min(32767, v))
        data.append(v)   # left
        data.append(v)   # right (стерео)

    buf = array.array('h', data)
    return pygame.mixer.Sound(buffer=buf)


class SoundManager:
    """
    Управляет звуковыми эффектами.
    Все звуки генерируются в __init__ — никаких файлов не нужно.
    """

    def __init__(self, sfx_on=True, music_on=True):
        self.sfx_on   = sfx_on
        self.music_on = music_on
        self.sounds   = {}
        self._ok      = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            self._build_sounds()
            self._ok = True
        except Exception as ex:
            print(f"[SoundManager] ошибка инициализации: {ex}")

    def _build_sounds(self):
        s = self.sounds
        s['pea_shoot']  = _gen(680,  80,  0.28)            # высокий «pew»
        s['gun_shoot']  = _gen(340,  55,  0.22)            # короткий «pop»
        s['punch']      = _gen(160, 110,  0.42, 'square')  # тупой удар
        s['zombie_die'] = _gen(360, 220,  0.32, 'descend') # нисходящий стон
        s['base_hit']   = _gen(90,  280,  0.50, 'square')  # низкий гулкий удар

    def play(self, name):
        if not self.sfx_on or not self._ok:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    # ------------------------------------------------------------------
    # Фоновая музыка — нужен файл sounds/music.ogg (или .mp3 / .wav)
    # ------------------------------------------------------------------

    def try_play_music(self):
        if not self.music_on or not self._ok:
            return
        for name in ('sounds/music.ogg', 'sounds/music.mp3', 'sounds/music.wav'):
            if os.path.exists(name):
                try:
                    pygame.mixer.music.load(name)
                    pygame.mixer.music.set_volume(0.38)
                    pygame.mixer.music.play(-1)
                    print(f"[Music] играет {name}")
                except Exception as ex:
                    print(f"[Music] не удалось загрузить {name}: {ex}")
                return
        # файл не найден — тихо пропускаем

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
