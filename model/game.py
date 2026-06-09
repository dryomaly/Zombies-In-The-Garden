# логика игры 

import json
import os

from settings import (STARTING_SUN, SUN_INTERVAL, SUN_AMOUNT, KILL_SUN,
                       PLANT_COSTS, PROJECTILE_SPEED, PROJECTILE_SIZE,
                       TILE_SIZE, PEASHOOTER)
from model.tile_map import TileMap
from model.base import Base
from model.zombie import Zombie, ZombieState
from model.plant import create_plant
from model.projectile import Projectile
from model.wave_manager import WaveManager
from model.spatial_grid import SpatialGrid


class GameModel:

    def __init__(self, level_num):
        path = os.path.join("data", "levels", f"level{level_num}.json")
        with open(path, "r", encoding="utf-8") as f:
            level_data = json.load(f)

        self.level_num = level_num
        self.level_name = level_data.get("name", f"Уровень {level_num}")

        self.tile_map = TileMap(level_data)

        self.path_pixels = [
            self.tile_map.cell_to_pixel(c, r)
            for c, r in self.tile_map.path
        ]

        self.base = Base(self.tile_map.base_pos)

        self.plants = {}
        self.zombies = []
        self.projectiles = []

        self.wave_manager = WaveManager(level_data["waves"])

        self.spatial_grid = SpatialGrid(cell_size=TILE_SIZE * 2)

        # счёт
        self.sun  = STARTING_SUN
        self.sun_timer = SUN_INTERVAL
        self.score = 0
        self.kills = 0

        self.selected_plant = None

        self.state = "playing"
        self.paused = False

        self.pending_sounds = []


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


    def _update_sun(self, dt):
        # Автоматическое начисление очковв
        self.sun_timer -= dt
        if self.sun_timer <= 0:
            self.sun      += SUN_AMOUNT
            self.sun_timer = SUN_INTERVAL

    def _spawn_zombies(self, dt):
        # Спавн зомби
        ztype = self.wave_manager.update(dt)
        if ztype:
            z = Zombie(ztype, self.path_pixels)
            self.zombies.append(z)

    def _update_spatial_grid(self):
        self.spatial_grid.clear()
        for z in self.zombies:
            if z.is_vulnerable():
                self.spatial_grid.add(z)

    def _update_zombies(self, dt):
        # Обновляение статуса зомби
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
                self.sun += KILL_SUN
                self.pending_sounds.append('zombie_die')
                to_remove.append(z)

        for z in to_remove:
            self.zombies.remove(z)

    def _update_plants(self, dt):
        # Обновление статуса растений
        for plant in self.plants.values():
            plant.update(dt)
            if not plant.can_attack():
                continue

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

                self.pending_sounds.append(
                    'pea_shoot' if plant.ptype == PEASHOOTER else 'gun_shoot'
                )
            else:
                target.take_damage(plant.damage)
                self.pending_sounds.append('punch')

    def _update_projectiles(self, dt):
        # Поведение снарядов
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


    def try_place_plant(self, col, row):
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
        pos = (col, row)
        if pos in self.plants:
            del self.plants[pos]

    def select_plant(self, ptype):
        if self.selected_plant == ptype:
            self.selected_plant = None
        else:
            self.selected_plant = ptype

    def deselect(self):
        self.selected_plant = None

    def toggle_pause(self):
        self.paused = not self.paused


    def _save_score(self):
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
        # Загрузка рекордов
        try:
            with open(os.path.join("data", "scores.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
