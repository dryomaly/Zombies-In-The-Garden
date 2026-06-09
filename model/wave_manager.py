# model/wave_manager.py — управление волнами зомби
#
# Алгоритм: взвешенный случайный выбор (weighted random)
# Используется когда волна содержит несколько типов зомби — случайно
# перемешиваем их с учётом весов (заданных в данных уровня).

import random


def weighted_choice(choices):
    total = sum(w for _, w in choices)
    r = random.uniform(0, total)
    cumulative = 0.0
    for item, weight in choices:
        cumulative += weight
        if r <= cumulative:
            return item
    return choices[-1][0]


class WaveManager:

    BETWEEN_WAVE_DELAY = 10.0
    SPAWN_INTERVAL = 2.5  
    FIRST_WAVE_DELAY = 5.0  

    def __init__(self, waves_data):
        self.waves = waves_data
        self.current_wave = 0
        self.spawn_timer = 0.0
        self.wave_timer = self.FIRST_WAVE_DELAY
        self.state = "countdown"
        self.spawn_queue = []
        self.wave_number = 0 

    
    def update(self, dt):
        # Возвращается тип зомби для спавна
        if self.state == "done":
            return None

        if self.state == "countdown":
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self._start_next_wave()
            return None

        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and self.spawn_queue:
            ztype = self.spawn_queue.pop(0)
            self.spawn_timer = self.SPAWN_INTERVAL

            if not self.spawn_queue:
                if self.current_wave >= len(self.waves):
                    self.state = "done"
                else:
                    self.state = "countdown"
                    self.wave_timer = self.BETWEEN_WAVE_DELAY

            return ztype

        return None


    def _start_next_wave(self):
        if self.current_wave >= len(self.waves):
            self.state = "done"
            return

        wave = self.waves[self.current_wave]
        self.current_wave += 1
        self.wave_number = self.current_wave

        pool = []
        for group in wave:
            ztype = group["type"]
            count = group["count"]
            weight = group.get("weight", 1.0)
            pool.extend([(ztype, weight)] * count)

        self.spawn_queue = []
        pool_copy = pool[:]
        while pool_copy:
            chosen = weighted_choice(pool_copy)
            self.spawn_queue.append(chosen)
            for i, (t, w) in enumerate(pool_copy):
                if t == chosen:
                    pool_copy.pop(i)
                    break

        self.state = "spawning"
        self.spawn_timer = 1.0


    def all_done(self):
        return self.state == "done" and len(self.spawn_queue) == 0

    def get_wave_display(self):
        return f"{self.wave_number} / {len(self.waves)}"

    def get_countdown(self):
        if self.state == "countdown":
            return max(0, int(self.wave_timer) + 1)
        return 0
