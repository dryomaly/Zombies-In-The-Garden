# Класс png-спрайтов

import pygame
import os

_cache: dict = {}

SPRITES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sprites")


def _load(path, size=None):
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
    path = os.path.join(SPRITES_DIR, "plants", f"{ptype}.png")
    return _load(path, size)


def load_zombie_sprite(ztype: str, size=(64, 64)):
    path = os.path.join(SPRITES_DIR, "zombies", f"{ztype}.png")
    return _load(path, size)


def sprites_available() -> bool:
    return os.path.isdir(SPRITES_DIR)


# def clear_cache():
#     """Очищает кэш (полезно при горячей перезагрузке спрайтов)."""
#     _cache.clear()
