# Обработка клавомыши

import pygame
from settings import SHOP_Y, SHOP_H, GRID_Y, PEASHOOTER, BOXER, MACHINEGUN

PLANT_TYPES  = [PEASHOOTER, BOXER, MACHINEGUN]
SHOP_CARD_W  = 130

_SC_Q      = 20
_SC_W      = 26
_SC_E      = 8
_SC_P      = 19
_SC_ESCAPE = 41


def _pressed(event, scancode, *keys):
    if event.scancode == scancode:
        return True
    return event.key in keys


def is_pause(event):
    return _pressed(event, _SC_P, pygame.K_p, ord("p"), ord("P"), ord("з"), ord("З"))


class InputHandler:
    def handle(self, events, model):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._handle_key(event, model)
            elif event.type == pygame.MOUSEBUTTONDOWN and not model.paused:
                if event.button == 1:
                    self._handle_left_click(event.pos, model)
                elif event.button == 3:
                    model.deselect()

    def _handle_key(self, event, model):
        if _pressed(event, _SC_ESCAPE, pygame.K_ESCAPE):
            if model.selected_plant:
                model.deselect()
        elif _pressed(event, _SC_Q, pygame.K_q, ord("q"), ord("Q"), ord("й"), ord("Й")):
            model.select_plant(PEASHOOTER)
        elif _pressed(event, _SC_W, pygame.K_w, ord("w"), ord("W"), ord("ц"), ord("Ц")):
            model.select_plant(BOXER)
        elif _pressed(event, _SC_E, pygame.K_e, ord("e"), ord("E"), ord("у"), ord("У")):
            model.select_plant(MACHINEGUN)

    def _handle_left_click(self, pos, model):
        mx, my = pos
        if SHOP_Y <= my <= SHOP_Y + SHOP_H:
            self._click_shop(mx, model)
        elif my >= GRID_Y:
            cell = model.tile_map.pixel_to_cell(mx, my)
            if cell:
                model.try_place_plant(cell[0], cell[1])

    def _click_shop(self, mx, model):
        for i, ptype in enumerate(PLANT_TYPES):
            cx = 10 + i * (SHOP_CARD_W + 10)
            if cx <= mx <= cx + SHOP_CARD_W:
                model.select_plant(ptype)
                return
