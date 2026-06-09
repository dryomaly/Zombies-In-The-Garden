# model/game.py — главная игровая модель (слой Model в MVC)
#
# GameModel хранит всё игровое состояние и содержит логику обновления.
# НЕ содержит ничего, связанного с отрисовкой (pygame.draw, Surface и т.д.).

import json
import os

from settings import (STARTING_SUN, SUN_INTERVAL, SUN_AMOUNT, KILL_SUN,
                       PLANT_COSTS, PROJECTILE_SPEED, PROJECTILE_SIZE,
                       TILE_SIZE, PEASHOOTER)
from model.tile_map   import TileMap
from model.base       import Base
from model.zombie     import Zombie, ZombieState
from model.plant      import create_plant
from model.projectile import Projectile
from model.wave_manager import WaveManager
from model.spatial_grid import SpatialGrid


class GameModel:
    """
    Вся игровая логика для одного уровня.
    Состояния: 'playing' | 'paused' | 'game_over' | 'win'
    """

    def __init__(self, level_num):
        # Загружаем данные уровня из JSON
        path = os.path.join("data", "levels", f"level{level_num}.json")
        with open(path, "r", encoding="utf-8") as f:
            level_data = json.load(f)

        self.level_num  = level_num
        self.level_name = level_data.get("name", f"Уровень {level_num}")

        # Карта
        self.tile_map = TileMap(level_data)

        # Путь зомби переводим из тайловых координат в пиксельные
        self.path_pixels = [
            self.tile_map.cell_to_pixel(c, r)
            for c, r in self.tile_map.path
        ]

        # База
        self.base = Base(self.tile_map.base_pos)

        # Игровые объекты
        self.plants      = {}   # (col, row) -> Plant
        self.zombies     = []   # list[Zombie]
        self.projectiles = []   # list[Projectile]

        # Волны
        self.wave_manager = WaveManager(level_data["waves"])

        # Пространственная сетка для быстрого поиска зомби рядом с растением
        self.spatial_grid = SpatialGrid(cell_size=TILE_SIZE * 2)

        # Ресурсы и счёт
        self.sun          = STARTING_SUN
        self.sun_timer    = SUN_INTERVAL
        self.score        = 0
        self.kills        = 0

        # Выбранный тип растения для постановки (None = не выбрано)
        self.selected_plant = None

        # Состояние игры
        self.state  = "playing"   # playing | paused | game_over | win
        self.paused = False

        # Список звуков для воспроизведения (main.py читает и очищает каждый кадр)
        self.pending_sounds = []

    # ==================================================================
    # Главный цикл обновления
    # ==================================================================

    def update(self, dt):
        if self.state != "playing" or self.paused:
            return

        self._update_sun(dt)
        self._spawn_zombies(dt)
        self._update_spatial_grid()
        self._update_zombies(dt)
        self._update_plants(dt)
        self._update_projectiles(dt)
        self._check_end_conditions()

    # ------------------------------------------------------------------

    def _update_sun(self, dt):
        """Автоматическое начисление солнца."""
        self.sun_timer -= dt
        if self.sun_timer <= 0:
            self.sun      += SUN_AMOUNT
            self.sun_timer = SUN_INTERVAL

    def _spawn_zombies(self, dt):
        """Запрашиваем у WaveManager: нужно ли спавнить зомби."""
        ztype = self.wave_manager.update(dt)
        if ztype:
            z = Zombie(ztype, self.path_pixels)
            self.zombies.append(z)

    def _update_spatial_grid(self):
        """Перестраиваем пространственную сетку по текущим позициям зомби."""
        self.spatial_grid.clear()
        for z in self.zombies:
            if z.is_vulnerable():
                self.spatial_grid.add(z)

    def _update_zombies(self, dt):
        """Обновляем зомби, убираем дошедших до базы и мёртвых."""
        to_remove = []
        for z in self.zombies:
            z.update(dt)
            if z.reached_base:
                self.base.take_damage(z.base_damage)
                self.pending_sounds.append('base_hit')
                to_remove.append(z)
            elif z.is_dead():
                self.kills += 1
                self.score += 10
                self.sun   += KILL_SUN
                self.pending_sounds.append('zombie_die')
                to_remove.append(z)

        for z in to_remove:
            self.zombies.remove(z)

    def _update_plants(self, dt):
        """Обновляем кулдауны растений, проводим атаки."""
        for plant in self.plants.values():
            plant.update(dt)
            if not plant.can_attack():
                continue

            # Запрашиваем зомби в радиусе через spatial_grid
            nearby = self.spatial_grid.query_radius(plant.x, plant.y, plant.range_px)
            target = plant.get_target(nearby)
            if target is None:
                continue

            plant.do_attack()

            if plant.has_projectile:
                proj = Projectile(
                    plant.ptype,
                    plant.x, plant.y,
                    target.x, target.y,
                    plant.damage,
                    PROJECTILE_SPEED[plant.ptype],
                    PROJECTILE_SIZE[plant.ptype],
                )
                self.projectiles.append(proj)
                # Звук выстрела
                self.pending_sounds.append(
                    'pea_shoot' if plant.ptype == PEASHOOTER else 'gun_shoot'
                )
            else:
                # Боксёр: мгновенный урон + анимация удара
                target.take_damage(plant.damage)
                self.pending_sounds.append('punch')

    def _update_projectiles(self, dt):
        """Двигаем снаряды, убираем те что вылетели за экран или попали."""
        to_remove = []
        for proj in self.projectiles:
            proj.update(dt, self.zombies)
            if not proj.active or proj.is_out_of_bounds():
                to_remove.append(proj)
        for proj in to_remove:
            self.projectiles.remove(proj)

    def _check_end_conditions(self):
        if self.base.is_dead():
            self.state = "game_over"
            self._save_score()
        elif self.wave_manager.all_done() and len(self.zombies) == 0:
            self.state = "win"
            self._save_score()

    # ==================================================================
    # Действия игрока
    # ==================================================================

    def try_place_plant(self, col, row):
        """
        Попытка поставить выбранное растение в клетку (col, row).
        Возвращает True если успешно.
        """
        if self.selected_plant is None:
            return False
        pos = (col, row)
        if pos not in self.tile_map.plantable:
            return False
        if pos in self.plants:
            return False
        cost = PLANT_COSTS[self.selected_plant]
        if self.sun < cost:
            return False

        self.sun -= cost
        self.plants[pos] = create_plant(self.selected_plant, col, row)
        return True

    def remove_plant(self, col, row):
        """Убрать растение с клетки (если оно там есть)."""
        pos = (col, row)
        if pos in self.plants:
            del self.plants[pos]

    def select_plant(self, ptype):
        """Выбрать тип растения. Повторный клик — снять выбор."""
        if self.selected_plant == ptype:
            self.selected_plant = None
        else:
            self.selected_plant = ptype

    def deselect(self):
        self.selected_plant = None

    def toggle_pause(self):
        self.paused = not self.paused

    # ==================================================================
    # Сохранение рекорда
    # ==================================================================

    def _save_score(self):
        """Сохраняем лучший счёт для уровня в data/scores.json."""
        score_path = os.path.join("data", "scores.json")
        try:
            with open(score_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        key = f"level{self.level_num}"
        if self.state == "win":
            if key not in data or data[key] < self.score:
                data[key] = self.score

        with open(score_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_scores():
        """Загружает сохранённые рекорды."""
        try:
            with open(os.path.join("data", "scores.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
