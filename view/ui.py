# view/ui.py — экраны меню (без эмодзи и спецсимволов, совместимо с любой ОС)

import pygame
from settings import SCREEN_W, SCREEN_H, WHITE, YELLOW, RED, DARK_GREEN, GRASS_DARK


def _btn(screen, text, x, y, w, h, font,
         color=(50,110,25), hover=(80,155,40)):
    mx, my = pygame.mouse.get_pos()
    over = x <= mx <= x+w and y <= my <= y+h
    pygame.draw.rect(screen, hover if over else color, (x,y,w,h), border_radius=10)
    pygame.draw.rect(screen, DARK_GREEN, (x,y,w,h), 2, border_radius=10)
    t = font.render(text, True, WHITE)
    screen.blit(t, (x+w//2-t.get_width()//2, y+h//2-t.get_height()//2))
    return over


def _clicked(events, x, y, w, h):
    mx, my = pygame.mouse.get_pos()
    for e in events:
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if x <= mx <= x+w and y <= my <= y+h:
                return True
    return False


def _bg(screen, title=None):
    screen.fill((22, 58, 10))
    pygame.draw.rect(screen, (30,75,18), (0, SCREEN_H-180, SCREEN_W, 180))
    for i in range(0, SCREEN_W, 40):
        h = 15 + (i % 3)*8
        pygame.draw.polygon(screen, (45,100,22),
                            [(i, SCREEN_H-180), (i+20, SCREEN_H-180-h), (i+40, SCREEN_H-180)])
    if title:
        f = pygame.font.SysFont("Arial", 50, bold=True)
        t = f.render(title, True, (175,240,95))
        screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 60))


# ─────────────────────────────────────────
def draw_menu(screen, events):
    _bg(screen)
    f1 = pygame.font.SysFont("Arial", 58, bold=True)
    f2 = pygame.font.SysFont("Arial", 22)
    fb = pygame.font.SysFont("Arial", 28, bold=True)

    t = f1.render("Zombies in the Garden", True, (180,245,100))
    screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 130))
    s = f2.render("Защити свой огород от нашествия зомби!", True, (140,195,80))
    screen.blit(s, (SCREEN_W//2 - s.get_width()//2, 200))

    bw, bh = 300, 62
    bx = SCREEN_W//2 - bw//2
    items = [
        ("Выбор уровня", "level_select", (50,110,25), (80,155,40)),
        ("Настройки",    "settings",     (40,90,110),  (60,130,155)),
        ("Выход",        "quit",         (110,40,40),  (155,60,60)),
    ]
    for i, (label, action, col, hov) in enumerate(items):
        by = 280 + i*88
        _btn(screen, label, bx, by, bw, bh, fb, color=col, hover=hov)
        if _clicked(events, bx, by, bw, bh):
            return action
    return None


# ─────────────────────────────────────────
def draw_level_select(screen, events, scores=None):
    if scores is None:
        scores = {}
    _bg(screen, "Выбор уровня")
    fb  = pygame.font.SysFont("Arial", 24, bold=True)
    fs  = pygame.font.SysFont("Arial", 17)
    fbk = pygame.font.SysFont("Arial", 20)

    levels = [
        ("Уровень 1", "Первые шаги"),
        ("Уровень 2", "Всё серьёзнее"),
        ("Уровень 3", "Последний рубеж"),
    ]
    cw, ch = 240, 165
    total_w = len(levels)*(cw+20)-20
    sx = SCREEN_W//2 - total_w//2
    cy_card = SCREEN_H//2 - ch//2 - 10
    mx, my = pygame.mouse.get_pos()

    for i, (name, sub1) in enumerate(levels):
        cx = sx + i*(cw+20)
        over = cx <= mx <= cx+cw and cy_card <= my <= cy_card+ch
        col  = (65,125,38) if over else (42,88,22)
        brd  = (115,195,58) if over else DARK_GREEN

        pygame.draw.rect(screen, col, (cx, cy_card, cw, ch), border_radius=12)
        pygame.draw.rect(screen, brd, (cx, cy_card, cw, ch), 2, border_radius=12)

        t = fb.render(name, True, WHITE)
        screen.blit(t, (cx+cw//2-t.get_width()//2, cy_card+18))
        for j, desc in enumerate([sub1]):
            d = fs.render(desc, True, (175,220,135))
            screen.blit(d, (cx+cw//2-d.get_width()//2, cy_card+60+j*26))

        key = f"level{i+1}"
        if key in scores:
            sc = fs.render(f"Рекорд: {scores[key]}", True, YELLOW)
            screen.blit(sc, (cx+cw//2-sc.get_width()//2, cy_card+128))

        if _clicked(events, cx, cy_card, cw, ch):
            return f"level_{i+1}"

    _btn(screen, "< Назад", 20, 20, 130, 42, fbk)
    if _clicked(events, 20, 20, 130, 42):
        return "back"
    return None


# ─────────────────────────────────────────
def draw_settings(screen, events, settings):
    _bg(screen, "Настройки")
    fb  = pygame.font.SysFont("Arial", 24, bold=True)
    fl  = pygame.font.SysFont("Arial", 22)
    fbk = pygame.font.SysFont("Arial", 20)

    items = [
        ("Музыка", "music"),
        ("Звуковые эффекты", "sounds"),
    ]

    for i, (label, key) in enumerate(items):
        y = 210 + i*88
        val = settings.get(key, True)

        lbl = fl.render(label, True, WHITE)
        screen.blit(lbl, (SCREEN_W//2 - 240, y+10))

        # Простые метки без спецсимволов
        btn_txt = "  ВКЛ  " if val else "  ВЫКЛ "
        btn_col = (36,108,36) if val else (108,36,36)
        btn_hov = (52,142,52) if val else (142,52,52)
        _btn(screen, btn_txt, SCREEN_W//2+60, y, 155, 48, fb,
             color=btn_col, hover=btn_hov)
        if _clicked(events, SCREEN_W//2+60, y, 155, 48):
            settings[key] = not val

    # # Подсказка про музыку
    # f_note = pygame.font.SysFont("Arial", 15)
    # note = f_note.render("Для музыки положи файл  sounds/music.ogg  рядом с main.py", True, (130,180,90))
    # screen.blit(note, (SCREEN_W//2 - note.get_width()//2, SCREEN_H - 220))

    _btn(screen, "< Назад", 20, 20, 130, 42, fbk)
    if _clicked(events, 20, 20, 130, 42):
        return "back"
    return None


# ─────────────────────────────────────────
def _overlay(screen):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 155))
    screen.blit(ov, (0, 0))


def draw_game_over(screen, events, score=0):
    _overlay(screen)
    fb = pygame.font.SysFont("Arial", 68, bold=True)
    fm = pygame.font.SysFont("Arial", 26)
    ft = pygame.font.SysFont("Arial", 26, bold=True)

    t = fb.render("ПОРАЖЕНИЕ!", True, (225,45,45))
    screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 225))
    s = fm.render("База уничтожена...", True, (200,140,140))
    screen.blit(s, (SCREEN_W//2 - s.get_width()//2, 315))
    sc = fm.render(f"Счёт: {score}", True, WHITE)
    screen.blit(sc, (SCREEN_W//2 - sc.get_width()//2, 358))

    bw, bh = 230, 58
    _btn(screen, "Повторить",    SCREEN_W//2-bw-15, 425, bw, bh, ft)
    _btn(screen, "Главное меню", SCREEN_W//2+15,    425, bw, bh, ft)
    if _clicked(events, SCREEN_W//2-bw-15, 425, bw, bh): return "retry"
    if _clicked(events, SCREEN_W//2+15,    425, bw, bh): return "menu"
    return None


def draw_win(screen, events, score=0, next_level_exists=True):
    _overlay(screen)
    fb = pygame.font.SysFont("Arial", 68, bold=True)
    fm = pygame.font.SysFont("Arial", 26)
    ft = pygame.font.SysFont("Arial", 26, bold=True)

    t = fb.render("ПОБЕДА!", True, (95,220,45))
    screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 225))
    s = fm.render("Все волны отбиты! Огород спасён!", True, (155,225,100))
    screen.blit(s, (SCREEN_W//2 - s.get_width()//2, 315))
    sc = fm.render(f"Счёт: {score}", True, WHITE)
    screen.blit(sc, (SCREEN_W//2 - sc.get_width()//2, 358))

    bw, bh = 230, 58
    if next_level_exists:
        _btn(screen, "Следующий >>", SCREEN_W//2-bw-15, 425, bw, bh, ft)
        if _clicked(events, SCREEN_W//2-bw-15, 425, bw, bh): return "next"
    _btn(screen, "Главное меню", SCREEN_W//2+15, 425, bw, bh, ft)
    if _clicked(events, SCREEN_W//2+15, 425, bw, bh): return "menu"
    return None


def draw_pause_menu(screen, events):
    _overlay(screen)
    fb = pygame.font.SysFont("Arial", 68, bold=True)
    fm = pygame.font.SysFont("Arial", 22)
    ft = pygame.font.SysFont("Arial", 26, bold=True)

    t = fb.render("ПАУЗА", True, (255, 230, 60))
    screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 210))
    hint = fm.render("P — продолжить игру", True, (200, 200, 200))
    screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 310))

    bw, bh = 230, 58
    _btn(screen, "Продолжить",   SCREEN_W//2-bw-15, 380, bw, bh, ft)
    _btn(screen, "Главное меню", SCREEN_W//2+15,    380, bw, bh, ft)
    if _clicked(events, SCREEN_W//2-bw-15, 380, bw, bh): return "resume"
    if _clicked(events, SCREEN_W//2+15,    380, bw, bh): return "menu"
    return None
