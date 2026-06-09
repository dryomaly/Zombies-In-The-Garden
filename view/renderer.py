# view/renderer.py — слой View (MVC)
# Растения и зомби рисуются только через PNG-спрайты.
# Pygame-примитивы используются только для базы, снарядов и умирания.

import pygame
from settings import *
from model.zombie import ZombieState
from view.draw_entities import draw_zombie_hp_bar, draw_dying_effect, draw_base_icon
from view.sprite_loader import load_plant_sprite, load_zombie_sprite

_TOOLTIPS = {
    PEASHOOTER: ["Стрелок", "Урон: 10  |  Дальность: 3.5 тайла",
                 "Скорость: 1.0 атк/с  |  Тип: снаряд"],
    BOXER:      ["Боксёр",  "Урон: 25  |  Дальность: 1.2 тайла",
                 "Скорость: 1.5 атк/с  |  Тип: мгновенно"],
    MACHINEGUN: ["Пулемёт", "Урон: 8   |  Дальность: 4.5 тайла",
                 "Скорость: 1.5 атк/с  |  Тип: снаряд"],
}


class Renderer:
    def __init__(self):
        self.font_big   = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_tip   = pygame.font.SysFont("Arial", 15)

    # ==================================================================
    def draw(self, screen, model):
        screen.fill(GRASS_COLOR)
        self._draw_grid(screen, model)
        self._draw_plants(screen, model)
        self._draw_zombies(screen, model)
        self._draw_projectiles(screen, model)
        self._draw_hud(screen, model)
        self._draw_shop(screen, model)

    # ------------------------------------------------------------------
    def _draw_grid(self, screen, model):
        tm = model.tile_map
        for col in range(tm.cols):
            for row in range(tm.rows):
                x = GRID_X + col * TILE_SIZE
                y = GRID_Y + row * TILE_SIZE
                pos = (col, row)

                if pos == tm.base_pos:
                    pygame.draw.rect(screen, (172, 142, 98), (x, y, TILE_SIZE, TILE_SIZE))
                elif pos in tm.road_tiles:
                    pygame.draw.rect(screen, ROAD_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, ROAD_DARK,  (x, y, TILE_SIZE, TILE_SIZE), 2)
                    mx2 = x + TILE_SIZE // 2
                    my2 = y + TILE_SIZE // 2
                    pygame.draw.line(screen, ROAD_DARK, (mx2-6, my2), (mx2+6, my2), 1)
                elif pos in tm.plantable and pos not in model.plants:
                    pygame.draw.rect(screen, PLANTABLE_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, GRASS_DARK, (x, y, TILE_SIZE, TILE_SIZE), 1)
                else:
                    pygame.draw.rect(screen, GRASS_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, GRASS_DARK, (x, y, TILE_SIZE, TILE_SIZE), 1)

        # Домик базы
        bc, br = tm.base_pos
        draw_base_icon(screen,
                       GRID_X + bc*TILE_SIZE + TILE_SIZE//2,
                       GRID_Y + br*TILE_SIZE + TILE_SIZE//2,
                       model.base.hp_percent)

        # Подсветка клетки при наведении (выбрано растение)
        if model.selected_plant:
            mx, my = pygame.mouse.get_pos()
            cell = tm.pixel_to_cell(mx, my)
            if cell and cell in tm.plantable and cell not in model.plants:
                hx = GRID_X + cell[0]*TILE_SIZE
                hy = GRID_Y + cell[1]*TILE_SIZE
                ov = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                ov.fill((150, 230, 80, 110))
                screen.blit(ov, (hx, hy))
                # Превью спрайта под курсором
                spr = load_plant_sprite(model.selected_plant, (TILE_SIZE, TILE_SIZE))
                if spr:
                    tmp = spr.copy()
                    tmp.set_alpha(165)
                    screen.blit(tmp, (hx, hy))

        # Стрелка спауна
        sc, sr = tm.spawn
        sx = GRID_X + sc*TILE_SIZE + TILE_SIZE//2
        sy = GRID_Y + sr*TILE_SIZE + TILE_SIZE//2
        pygame.draw.polygon(screen, (200, 75, 75),
                            [(sx-10, sy), (sx+8, sy-8), (sx+8, sy+8)])

    # ------------------------------------------------------------------
    def _draw_plants(self, screen, model):
        for (col, row), plant in model.plants.items():
            cx = GRID_X + col*TILE_SIZE + TILE_SIZE//2
            cy = GRID_Y + row*TILE_SIZE + TILE_SIZE//2

            spr = load_plant_sprite(plant.ptype, (TILE_SIZE, TILE_SIZE))
            if spr:
                screen.blit(spr, (cx - TILE_SIZE//2, cy - TILE_SIZE//2))

            # Радиус атаки при наведении
            if not model.selected_plant:
                mx, my = pygame.mouse.get_pos()
                if abs(mx-cx) < TILE_SIZE//2 and abs(my-cy) < TILE_SIZE//2:
                    r = int(plant.range_px)
                    s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255,255,100,38),  (r+2, r+2), r)
                    pygame.draw.circle(s, (255,255,100,110), (r+2, r+2), r, 2)
                    screen.blit(s, (cx-r-2, cy-r-2))

    # ------------------------------------------------------------------
    def _draw_zombies(self, screen, model):
        for z in model.zombies:
            cx, cy = int(z.x), int(z.y)

            if z.state == ZombieState.DYING:
                draw_dying_effect(screen, cx, cy, z.die_progress)
                continue

            spr = load_zombie_sprite(z.ztype, (TILE_SIZE, TILE_SIZE))
            if spr:
                screen.blit(spr, (cx - TILE_SIZE//2, cy - TILE_SIZE//2))

            draw_zombie_hp_bar(screen, cx, cy, z.hp_percent)

    # ------------------------------------------------------------------
    def _draw_projectiles(self, screen, model):
        for proj in model.projectiles:
            col = PROJECTILE_COLOR[proj.ptype]
            px, py = int(proj.x), int(proj.y)
            pygame.draw.circle(screen, col, (px, py), proj.size)
            tx = int(proj.x - proj.vx * 0.04)
            ty = int(proj.y - proj.vy * 0.04)
            dark = (col[0]//2, col[1]//2, col[2]//2)
            pygame.draw.circle(screen, dark, (tx, ty), max(1, proj.size-3))

    # ------------------------------------------------------------------
    def _draw_hud(self, screen, model):
        pygame.draw.rect(screen, HUD_BG, (0, 0, SCREEN_W, GRID_Y))
        pygame.draw.line(screen, GRASS_DARK, (0, GRID_Y), (SCREEN_W, GRID_Y), 2)

        sun = self.font_big.render(f"Sun: {model.sun}", True, YELLOW)
        screen.blit(sun, (12, 10))

        wm = model.wave_manager
        if wm.state == "countdown" and wm.wave_number < len(wm.waves):
            wtxt = f"Волна {wm.wave_number+1}/{len(wm.waves)} через {wm.get_countdown()}с"
        else:
            wtxt = f"Волна {wm.wave_number}/{len(wm.waves)}"
        ws = self.font_med.render(wtxt, True, WHITE)
        screen.blit(ws, (SCREEN_W//2 - ws.get_width()//2, 14))

        hp = self.font_med.render(f"База: {model.base.hp}/{model.base.max_hp}",
                                  True, (220, 100, 100))
        screen.blit(hp, (SCREEN_W - hp.get_width() - 12, 14))

        # Только подсказка про паузу (остальные убраны)
        if model.selected_plant:
            tip = "ЛКМ — поставить  |  ПКМ / ESC — отмена  |  P — пауза"
        else:
            tip = "P — пауза"
        ts = self.font_small.render(tip, True, (145, 190, 105))
        screen.blit(ts, (SCREEN_W//2 - ts.get_width()//2, GRID_Y - 17))

    # ------------------------------------------------------------------
    def _draw_shop(self, screen, model):
        pygame.draw.rect(screen, SHOP_BG, (0, SHOP_Y, SCREEN_W, SHOP_H))
        pygame.draw.line(screen, GRASS_DARK, (0, SHOP_Y), (SCREEN_W, SHOP_Y), 2)

        card_w = 130
        card_h = SHOP_H - 16
        ptypes  = [PEASHOOTER, BOXER, MACHINEGUN]
        mx, my  = pygame.mouse.get_pos()
        tooltip_ptype = None

        for i, ptype in enumerate(ptypes):
            cx  = 10 + i*(card_w+10)
            cy  = SHOP_Y + 8
            sel = model.selected_plant == ptype
            can = model.sun >= PLANT_COSTS[ptype]

            bg  = SHOP_CARD_SEL if sel else SHOP_CARD_BG
            brd = (125, 215, 65) if sel else GRASS_DARK
            pygame.draw.rect(screen, bg,  (cx, cy, card_w, card_h), border_radius=8)
            pygame.draw.rect(screen, brd, (cx, cy, card_w, card_h), 2, border_radius=8)

            # Иконка — только PNG
            spr = load_plant_sprite(ptype, (52, 52))
            if spr:
                screen.blit(spr, (cx + card_w//2 - 26, cy + 4))

            ns = self.font_small.render(PLANT_NAMES[ptype], True, WHITE)
            screen.blit(ns, (cx + card_w//2 - ns.get_width()//2, cy + 60))

            cc = YELLOW if can else RED
            cs = self.font_small.render(f"Sun:{PLANT_COSTS[ptype]}", True, cc)
            screen.blit(cs, (cx + card_w//2 - cs.get_width()//2, cy + 78))

            keys = {PEASHOOTER:'Q', BOXER:'W', MACHINEGUN:'E'}
            ks = self.font_small.render(f"[{keys[ptype]}]", True, (130,180,90))
            screen.blit(ks, (cx + card_w//2 - ks.get_width()//2, cy + 96))

            hovered = cx <= mx <= cx+card_w and SHOP_Y <= my <= SHOP_Y+SHOP_H
            if hovered or sel:
                tooltip_ptype = ptype

        # Показываем тултип только если выбрано растение (selected_plant).
        # При отмене выбора (selected_plant is None) тултип скрывается.
        # Позиция тултипа привязана к центру карточки выбранного растения,
        # а НЕ к курсору мыши — плашка стоит над карточкой и не ёрзает.
        active_tooltip = model.selected_plant if model.selected_plant else tooltip_ptype
        if active_tooltip:
            # Вычисляем центр X карточки активного растения
            idx = ptypes.index(active_tooltip)
            card_cx = 10 + idx * (card_w + 10) + card_w // 2
            self._draw_tooltip(screen, active_tooltip, card_cx)

    def _draw_tooltip(self, screen, ptype, anchor_x):
        """
        Рисует плашку с информацией об растении.
        anchor_x — центр X карточки, к которой привязан тултип.
        Тултип всегда остаётся над своей карточкой, независимо от курсора.
        """
        lines = _TOOLTIPS[ptype]
        pad, lh, tip_w = 8, 18, 290
        tip_h = len(lines)*lh + pad*2
        # Центрируем тултип по X карточки, не даём вылезти за экран
        tip_x = min(max(0, anchor_x - tip_w // 2), SCREEN_W - tip_w)
        tip_y = SHOP_Y - tip_h - 6
        pygame.draw.rect(screen, (18, 44, 10), (tip_x, tip_y, tip_w, tip_h), border_radius=6)
        pygame.draw.rect(screen, (80, 150, 40), (tip_x, tip_y, tip_w, tip_h), 1, border_radius=6)
        for j, line in enumerate(lines):
            s = self.font_tip.render(line, True, YELLOW if j == 0 else WHITE)
            screen.blit(s, (tip_x + pad, tip_y + pad + j*lh))


