# controller/input_handler.py — обработка ввода (слой Controller в MVC)
# P-пауза обрабатывается в main.py, чтобы не было двойного срабатывания.

import pygame
from settings import SHOP_Y, SHOP_H, GRID_Y, PEASHOOTER, BOXER, MACHINEGUN
from controller.hotkeys import is_escape, is_peashooter, is_boxer, is_machinegun

PLANT_TYPES  = [PEASHOOTER, BOXER, MACHINEGUN]
SHOP_CARD_W  = 130


class InputHandler:
    def handle(self, events, model):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._handle_key(event, model)
            elif event.type == pygame.MOUSEBUTTONDOWN and not model.paused:
                # Клики мышью игнорируются на паузе
                if event.button == 1:
                    self._handle_left_click(event.pos, model)
                elif event.button == 3:
                    model.deselect()

    def _handle_key(self, event, model):
        if is_escape(event):
            if model.selected_plant:
                model.deselect()
        elif is_peashooter(event):
            model.select_plant(PEASHOOTER)
        elif is_boxer(event):
            model.select_plant(BOXER)
        elif is_machinegun(event):
            model.select_plant(MACHINEGUN)
        # P — пауза обрабатывается в main.py

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
            cx = 10 + i*(SHOP_CARD_W+10)
            if cx <= mx <= cx + SHOP_CARD_W:
                model.select_plant(ptype)
                return
