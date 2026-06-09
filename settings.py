# settings.py — все константы игры

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
CAPTION = "Зомби в огороде"

TILE_SIZE = 64
GRID_COLS = 18
GRID_ROWS = 8

# Сетка располагается по центру по горизонтали, под HUD
GRID_X = (SCREEN_W - GRID_COLS * TILE_SIZE) // 2   # = 64
GRID_Y = 60   # высота верхнего HUD

# Панель магазина внизу
SHOP_Y = GRID_Y + GRID_ROWS * TILE_SIZE   # = 572
SHOP_H = SCREEN_H - SHOP_Y                # = 148

# ---------- Цвета ----------
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0  )
GRAY         = (128, 128, 128)
DARK_GRAY    = (64,  64,  64 )
RED          = (210, 40,  40 )
DARK_RED     = (140, 0,   0  )
YELLOW       = (255, 215, 0  )
ORANGE       = (255, 140, 0  )
BROWN        = (101, 67,  33 )

DARK_GREEN      = (34,  85,  34 )

GRASS_COLOR     = (80,  120, 25 )
GRASS_DARK      = (55,  90,  15 )
ROAD_COLOR      = (195, 165, 105)
ROAD_DARK       = (155, 125, 75 )
PLANTABLE_COLOR = (95,  145, 38 )   # клетка рядом с дорогой (доступна для постановки)
PLANTABLE_HOVER = (115, 175, 50 )   # при наведении мыши

HUD_BG        = (30,  75,  30 )
SHOP_BG       = (18,  48,  8  )
SHOP_CARD_BG  = (38,  75,  18 )
SHOP_CARD_SEL = (65,  130, 35 )

# ---------- Типы растений ----------
PEASHOOTER = "peashooter"
BOXER      = "boxer"
MACHINEGUN = "machinegun"

PLANT_NAMES = {
    PEASHOOTER: "Стрелок",
    BOXER:      "Боксёр",
    MACHINEGUN: "Пулемёт",
}

PLANT_COSTS = {
    PEASHOOTER: 100,
    BOXER:      150,
    MACHINEGUN: 225,   # чуть дороже + нёрф характеристик
}

# damage — урон за выстрел/удар
# range  — радиус атаки в тайлах
# attack_rate — атак в секунду
# has_projectile — True: стреляет снарядом; False: мгновенный урон (Боксёр)
PLANT_STATS = {
    PEASHOOTER: {"damage": 10, "range": 3.5, "attack_rate": 1.0, "has_projectile": True},
    BOXER:      {"damage": 25, "range": 1.2, "attack_rate": 1.5, "has_projectile": False},
    MACHINEGUN: {"damage": 7,  "range": 4.5, "attack_rate": 2.0, "has_projectile": True},
    # Пулемёт нёрфнут: урон 12→8, дальность 5.5→4.5, скорость 2.5→1.5 атк/с
}

# ---------- Типы зомби ----------
ZOMBIE_NORMAL = "normal"
ZOMBIE_FAST   = "fast"

# speed        — скорость в тайлах/сек (умножается на TILE_SIZE → пиксели/сек)
# hp           — очки здоровья
# base_damage  — урон по базе при касании
ZOMBIE_STATS = {
    ZOMBIE_NORMAL: {"speed": 0.55, "hp": 100, "base_damage": 25},
    ZOMBIE_FAST:   {"speed": 1.6,  "hp": 40,  "base_damage": 10},
}

# ---------- Солнце ----------
STARTING_SUN = 200
SUN_INTERVAL = 8.0    # секунд между начислением
SUN_AMOUNT   = 25     # сколько начисляется
KILL_SUN     = 10     # за убийство зомби

# ---------- База ----------
BASE_MAX_HP  = 200

# ---------- Снаряды ----------
PROJECTILE_SPEED = {
    PEASHOOTER: 220,   # px/sec
    MACHINEGUN: 360,
}
PROJECTILE_SIZE = {
    PEASHOOTER: 8,
    MACHINEGUN: 5,
}
PROJECTILE_COLOR = {
    PEASHOOTER: (100, 210, 50),
    MACHINEGUN: (255, 210, 60),
}
