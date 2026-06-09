# view/sprite_loader.py — загрузка PNG-спрайтов вместо нарисованных примитивов
#
# КАК ИСПОЛЬЗОВАТЬ PNG СПРАЙТЫ:
# ─────────────────────────────
# 1. Создай папку  sprites/plants/  и  sprites/zombies/
# 2. Положи в них PNG файлы:
#
#    sprites/plants/peashooter.png   — Стрелок   (64×64 пикселя)
#    sprites/plants/boxer.png        — Боксёр    (64×64 пикселя)
#    sprites/plants/machinegun.png   — Пулемёт   (64×64 пикселя)
#    sprites/zombies/normal.png      — Обычный зомби  (64×64)
#    sprites/zombies/fast.png        — Быстрый зомби  (64×64)
#
# 3. Готово! Если файл найден — используется PNG.
#    Если нет — автоматически рисуется программная версия.
#
# СОВЕТЫ:
# • PNG должен иметь прозрачный фон (RGBA / 32-bit)
# • Размер 64×64 — по размеру тайла. Можно другой — масштабируется авто.

import pygame
import os

_cache: dict = {}

SPRITES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sprites')


def _load(path, size=None):
    """Загружает PNG, кэширует, масштабирует если нужно."""
    key = (path, size)
    if key in _cache:
        return _cache[key]

    if not os.path.exists(path):
        _cache[key] = None
        return None

    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        _cache[key] = img
        return img
    except Exception as e:
        print(f"[Sprites] ошибка загрузки {path}: {e}")
        _cache[key] = None
        return None


def load_plant_sprite(ptype: str, size=(64, 64)):
    """Возвращает Surface или None если спрайта нет."""
    path = os.path.join(SPRITES_DIR, 'plants', f'{ptype}.png')
    return _load(path, size)


def load_zombie_sprite(ztype: str, size=(64, 64)):
    """Возвращает Surface или None если спрайта нет."""
    path = os.path.join(SPRITES_DIR, 'zombies', f'{ztype}.png')
    return _load(path, size)


def sprites_available() -> bool:
    """True если папка sprites/ существует."""
    return os.path.isdir(SPRITES_DIR)


def clear_cache():
    """Очищает кэш (полезно при горячей перезагрузке спрайтов)."""
    _cache.clear()
