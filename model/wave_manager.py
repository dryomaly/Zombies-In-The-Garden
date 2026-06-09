# model/wave_manager.py — управление волнами зомби
#
# Алгоритм: взвешенный случайный выбор (weighted random)
# Используется когда волна содержит несколько типов зомби — случайно
# перемешиваем их с учётом весов (заданных в данных уровня).

import random


def weighted_choice(choices):
    """
    choices — список (item, weight).
    Возвращает случайный item пропорционально весу.
    """
    total = sum(w for _, w in choices)
    r = random.uniform(0, total)
    cumulative = 0.0
    for item, weight in choices:
        cumulative += weight
        if r <= cumulative:
            return item
    return choices[-1][0]


class WaveManager:
    """
    Управляет последовательностью волн зомби.

    waves_data — список волн (из JSON уровня).
    Каждая волна — список {"type": str, "count": int, "weight": float}.
    """

    BETWEEN_WAVE_DELAY = 10.0   # пауза между волнами (сек)
    SPAWN_INTERVAL     = 2.5    # пауза между зомби в волне (сек)
    FIRST_WAVE_DELAY   = 5.0    # пауза перед самой первой волной (сек)

    def __init__(self, waves_data):
        self.waves         = waves_data
        self.current_wave  = 0         # индекс следующей волны для запуска
        self.spawn_timer   = 0.0       # таймер до следующего спавна
        self.wave_timer    = self.FIRST_WAVE_DELAY
        self.state         = "countdown"   # countdown | spawning | done
        self.spawn_queue   = []        # очередь зомби для спавна в текущей волне

        # Для отображения в HUD
        self.wave_number   = 0         # номер текущей/последней волны (начиная с 1)

    # ------------------------------------------------------------------

    def update(self, dt):
        """
        Вызывается каждый кадр.
        Возвращает тип зомби для спавна (str) или None.
        """
        if self.state == "done":
            return None

        if self.state == "countdown":
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self._start_next_wave()
            return None

        # --- spawning ---
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and self.spawn_queue:
            ztype = self.spawn_queue.pop(0)
            self.spawn_timer = self.SPAWN_INTERVAL

            if not self.spawn_queue:
                # Волна закончила спавн
                if self.current_wave >= len(self.waves):
                    self.state = "done"
                else:
                    self.state      = "countdown"
                    self.wave_timer = self.BETWEEN_WAVE_DELAY

            return ztype

        return None

    # ------------------------------------------------------------------

    def _start_next_wave(self):
        if self.current_wave >= len(self.waves):
            self.state = "done"
            return

        wave = self.waves[self.current_wave]
        self.current_wave += 1
        self.wave_number = self.current_wave

        # Собираем пул зомби для спавна с учётом весов
        pool = []
        for group in wave:
            ztype  = group["type"]
            count  = group["count"]
            weight = group.get("weight", 1.0)
            pool.extend([(ztype, weight)] * count)

        # Взвешенно перемешиваем: строим новую очередь через weighted_choice
        self.spawn_queue = []
        pool_copy = pool[:]
        while pool_copy:
            chosen = weighted_choice(pool_copy)
            self.spawn_queue.append(chosen)
            # Удаляем один элемент с таким типом
            for i, (t, w) in enumerate(pool_copy):
                if t == chosen:
                    pool_copy.pop(i)
                    break

        self.state       = "spawning"
        self.spawn_timer = 1.0   # маленькая пауза перед первым зомби волны

    # ------------------------------------------------------------------

    def all_done(self):
        """Все волны отспавнились и очередь пуста."""
        return self.state == "done" and len(self.spawn_queue) == 0

    def get_wave_display(self):
        """Строка для HUD: 'Волна 2 / 3'."""
        return f"{self.wave_number} / {len(self.waves)}"

    def get_countdown(self):
        """Сколько секунд до следующей волны (для отображения)."""
        if self.state == "countdown":
            return max(0, int(self.wave_timer) + 1)
        return 0
