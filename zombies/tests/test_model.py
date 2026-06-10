# tests/test_model.py — юнит-тесты для модели.
# Покрывает: Base (HP, урон, смерть), create_plant (тип, снаряды, дальность,
# кулдаун атаки). Запуск: python -m pytest tests/ из корня проекта.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from model.game import Base
from model.entities import create_plant, Peashooter, Boxer, MachineGun
from settings import PEASHOOTER, BOXER, MACHINEGUN


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
    p.update(10.0)
    assert p.can_attack()
