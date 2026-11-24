import pygame

from ..scene import Scene
from ..ui import Button, bar, panel, text


class LegacyScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.message = ""
        self.buttons = [
            Button((150, 510, 240, 52), "Анализ −1 энергия", self.analyze),
            Button((410, 510, 240, 52), "Шаг подмены", self.replace),
            Button((670, 510, 240, 52), "Стабилизация −10", self.stabilize),
            Button((930, 510, 180, 52), "Назад", self.back),
        ]

    def analyze(self):
        state = self.game.state
        if state.energy <= 0:
            self.message = "Энергии нет. Даже легаси это заметило."
            return
        state.energy -= 1
        state.legacy.opacity = max(0, state.legacy.opacity - 20)
        self.message = "Анализ завершён. Непрозрачность снизилась."
        state.add_log(self.message)

    def replace(self):
        state = self.game.state
        legacy = state.legacy
        if legacy.status == "works":
            legacy.status = "replacing"
        if legacy.status != "replacing":
            self.message = "Подмена уже завершена или модуль сломан."
            return
        legacy.progress = min(100, legacy.progress + 25)
        legacy.cascade += max(1, legacy.opacity // 35)
        if legacy.progress >= 100:
            if legacy.cascade > self.game.config["game"]["legacy_cascade_limit"]:
                legacy.status = "broken"
                self.message = "Подмена закончена. Каскад тоже. Плохо."
            else:
                legacy.status = "replaced"
                self.message = "Легаси подменён. Одеяло слегка отпустило."
        else:
            self.message = f"Подмена {legacy.progress}%. Каскад: {legacy.cascade}."
        state.add_log(self.message)

    def stabilize(self):
        state = self.game.state
        if state.budget < 10:
            self.message = "Бюджета не хватает даже на скотч."
            return
        state.budget -= 10
        state.legacy.cascade = max(0, state.legacy.cascade - 4)
        if state.legacy.status == "broken" and state.legacy.cascade == 0:
            state.legacy.status = "replaced"
        self.message = "Стабилизация проведена. Красное облако стало меньше."
        state.add_log(self.message)

    def back(self):
        from .office import OfficeScene
        self.game.change_scene(OfficeScene(self.game))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()

    def draw(self, surface):
        colors, fonts, legacy = self.game.colors, self.game.fonts, self.game.state.legacy
        surface.fill((35, 24, 32))
        text(surface, "ЛЕГАСИ-МОНОЛИТ", (640, 75), fonts["title"], colors["red"], True)
        panel(surface, pygame.Rect(260, 140, 760, 300), colors, (47, 34, 49))
        text(surface, f"статус: {legacy.status}", (640, 190), fonts["heading"], colors["text"], True)
        text(surface, f"непрозрачность: {legacy.opacity}", (640, 235), fonts["body"], colors["muted"], True)
        text(surface, f"каскад ошибок: {legacy.cascade}", (640, 280), fonts["heading"], colors["red"], True)
        bar(surface, pygame.Rect(390, 335, 500, 25), legacy.progress, 100, colors["accent"], colors)
        text(surface, f"подмена: {legacy.progress}%", (640, 375), fonts["small"], colors["text"], True)
        text(surface, self.message, (640, 460), fonts["body"], colors["yellow"], True)
        for button in self.buttons:
            button.draw(surface, fonts["small"], colors)
