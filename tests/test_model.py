# tests/test_model.py — юнит-тесты для игровой логики
#
# Запуск: pytest tests/ -v
# (из директории pvz/)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from model.pathfinder  import astar
from model.spatial_grid import SpatialGrid
from model.base         import Base
from model.zombie       import Zombie, ZombieState
from model.plant        import create_plant, Peashooter, Boxer, MachineGun
from model.projectile   import Projectile, _rects_overlap
from settings           import PEASHOOTER, BOXER, MACHINEGUN, TILE_SIZE, GRID_X, GRID_Y


# ─────────────────────────────────────────────────
# A* алгоритм
# ─────────────────────────────────────────────────

def test_astar_straight_path():
    passable = {(c, 0) for c in range(6)}  # горизонтальный коридор
    path = astar(passable, (0, 0), (5, 0), 10, 5)
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (5, 0)
    assert len(path) == 6


def test_astar_l_shape():
    passable = {(c, 0) for c in range(4)} | {(3, r) for r in range(4)}
    path = astar(passable, (0, 0), (3, 3), 6, 6)
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (3, 3)
    # Все шаги только горизонтальные или вертикальные
    for i in range(len(path) - 1):
        dc = abs(path[i+1][0] - path[i][0])
        dr = abs(path[i+1][1] - path[i][1])
        assert dc + dr == 1, "A* шагает только по 4 направлениям"


def test_astar_no_path():
    passable = {(0, 0), (2, 0)}   # разрыв на (1, 0)
    path = astar(passable, (0, 0), (2, 0), 4, 2)
    assert path is None


def test_astar_start_equals_goal():
    passable = {(0, 0)}
    path = astar(passable, (0, 0), (0, 0), 5, 5)
    assert path is not None
    assert path == [(0, 0)]


# ─────────────────────────────────────────────────
# AABB коллизия
# ─────────────────────────────────────────────────

def test_rects_overlap_yes():
    r1 = (0, 0, 10, 10)
    r2 = (5, 5, 10, 10)
    assert _rects_overlap(r1, r2) is True


def test_rects_overlap_no():
    r1 = (0, 0, 10, 10)
    r2 = (20, 20, 10, 10)
    assert _rects_overlap(r1, r2) is False


def test_rects_overlap_touching_edge():
    # Касание — не пересечение
    r1 = (0, 0, 10, 10)
    r2 = (10, 0, 10, 10)
    assert _rects_overlap(r1, r2) is False


# ─────────────────────────────────────────────────
# База
# ─────────────────────────────────────────────────

def test_base_initial_hp():
    base = Base((5, 5))
    assert base.hp == base.max_hp
    assert not base.is_dead()
    assert base.hp_percent == 1.0


def test_base_damage():
    base = Base((0, 0))
    base.take_damage(50)
    assert base.hp == base.max_hp - 50
    assert not base.is_dead()


def test_base_overkill():
    base = Base((0, 0))
    base.take_damage(99999)
    assert base.hp == 0
    assert base.is_dead()


# ─────────────────────────────────────────────────
# FSM зомби
# ─────────────────────────────────────────────────

def _make_zombie(ztype="normal"):
    """Зомби с простым путём из 3 точек."""
    path = [(100, 100), (200, 100), (300, 100)]
    return Zombie(ztype, path)


def test_zombie_initial_state():
    z = _make_zombie()
    assert z.state == ZombieState.WALKING
    assert z.hp == z.max_hp
    assert not z.is_dead()
    assert z.is_vulnerable()


def test_zombie_take_damage():
    z = _make_zombie()
    z.take_damage(30)
    assert z.hp == z.max_hp - 30
    assert z.state == ZombieState.WALKING


def test_zombie_fsm_dying():
    z = _make_zombie()
    z.take_damage(9999)
    assert z.state == ZombieState.DYING
    assert not z.is_dead()
    assert not z.is_vulnerable()


def test_zombie_fsm_dead():
    z = _make_zombie()
    z.take_damage(9999)
    # Ждём окончания анимации
    z.update(1.0)
    assert z.state == ZombieState.DEAD
    assert z.is_dead()


def test_zombie_no_damage_when_dying():
    z = _make_zombie()
    z.take_damage(9999)       # начинает умирать
    hp_before = z.hp
    z.take_damage(50)         # должно игнорироваться
    assert z.hp == hp_before


def test_zombie_reaches_base():
    """Зомби доходит до конца пути."""
    path = [(100, 100)]   # один тайл — сразу база
    z = Zombie("normal", path)
    # path_index начинается с 1, что уже >= len(path)
    z.update(0.016)
    assert z.reached_base is True


def test_zombie_direction():
    path = [(100, 200), (200, 200)]
    z = Zombie("normal", path)
    assert z.direction == (1, 0)   # движется вправо


# ─────────────────────────────────────────────────
# Пространственная сетка
# ─────────────────────────────────────────────────

class _FakeObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_spatial_grid_query_finds_nearby():
    sg = SpatialGrid(cell_size=64)
    a = _FakeObj(100, 100)
    b = _FakeObj(500, 500)
    sg.add(a)
    sg.add(b)
    result = sg.query_radius(100, 100, 50)
    assert a in result
    assert b not in result


def test_spatial_grid_empty():
    sg = SpatialGrid(cell_size=64)
    result = sg.query_radius(0, 0, 1000)
    assert result == []


def test_spatial_grid_clear():
    sg = SpatialGrid(cell_size=64)
    sg.add(_FakeObj(50, 50))
    sg.clear()
    result = sg.query_radius(50, 50, 100)
    assert result == []


# ─────────────────────────────────────────────────
# Растения
# ─────────────────────────────────────────────────

def test_plant_factory():
    p = create_plant(PEASHOOTER, 3, 4)
    assert isinstance(p, Peashooter)
    assert p.col == 3 and p.row == 4
    assert p.has_projectile is True


def test_boxer_no_projectile():
    b = create_plant(BOXER, 1, 1)
    assert isinstance(b, Boxer)
    assert b.has_projectile is False


def test_machinegun_range():
    mg = create_plant(MACHINEGUN, 0, 0)
    assert isinstance(mg, MachineGun)
    assert mg.range_px > create_plant(PEASHOOTER, 0, 0).range_px


def test_plant_attack_cooldown():
    p = create_plant(PEASHOOTER, 0, 0)
    assert p.can_attack()
    p.do_attack()
    assert not p.can_attack()
    p.update(10.0)   # пропускаем время
    assert p.can_attack()


# ─────────────────────────────────────────────────
# Снаряд
# ─────────────────────────────────────────────────

def test_projectile_moves():
    proj = Projectile(PEASHOOTER, 0, 0, 100, 0, 10, 200, 6)
    old_x = proj.x
    proj.update(0.1, [])
    assert proj.x > old_x


def test_projectile_hits_zombie():
    # Снаряд медленно летит в зомби (не перескакивает через него за 1 кадр)
    path = [(300, 100), (400, 100)]
    z = Zombie("normal", path)
    z.x, z.y = 300.0, 100.0

    # Снаряд стартует в 15px от зомби, скорость 80px/s → за 0.2с пройдёт 16px
    # Зомби в 15px → попадание гарантировано
    proj = Projectile(PEASHOOTER, 285, 100, 300, 100, 10, 80, 8)
    old_hp = z.hp
    proj.update(0.2, [z])
    assert z.hp < old_hp or not proj.active
