import random
import pygame

from ..scene import Scene
from ..ui import Button, gradient_background, panel, text


class SyncScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.answers = []
        self.result = ""
        self.buttons = [Button((390, 540, 500, 52), "Задать вопрос трём командам", self.ask), Button((540, 610, 200, 45), "Назад", self.back)]

    def ask(self):
        state = self.game.state
        chosen = random.sample(state.teams[:5], 3)
        self.answers = []
        for team in chosen:
            honest = random.randint(1, 100) <= team.honesty
            value = team.readiness if honest else min(100, team.readiness + random.randint(15, 30))
            self.answers.append((team, value, honest))
        values = [value for _, value, _ in self.answers]
        if max(values) - min(values) >= 15:
            liar = max(self.answers, key=lambda item: item[1])[0]
            liar.suspicion = min(100, liar.suspicion + 25)
            state.karma = min(100, state.karma + 3)
            self.result = f"Ответы расходятся. Подозрение: {liar.name}. Нажатие «Давить» окупилось."
        else:
            self.result = "Ответы сходятся. Возможно, все просто одинаково устали."
        state.add_log("Синхронизация проведена: " + self.result)

    def back(self):
        from .office import OfficeScene
        self.game.change_scene(OfficeScene(self.game))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()

    def draw(self, surface):
        colors, fonts = self.game.colors, self.game.fonts
        gradient_background(surface, colors)
        text(surface, "СИНХРОНИЗАЦИЯ И ЛОЖЬ", (640, 70), fonts["title"], colors["accent"], True)
        text(surface, "Один вопрос. Три ответа. И ни одного общего календаря.", (640, 120), fonts["body"], colors["muted"], True)
        for index, (team, value, _) in enumerate(self.answers):
            x = 110 + index * 370
            panel(surface, pygame.Rect(x, 185, 320, 250), colors)
            text(surface, team.name, (x + 160, 225), fonts["heading"], colors["text"], True)
            text(surface, f"готовность: {value}%", (x + 160, 300), fonts["body"], colors["yellow"], True)
            text(surface, f"подозрение: {team.suspicion}", (x + 160, 345), fonts["small"], colors["red"], True)
        text(surface, self.result, (640, 480), fonts["body"], colors["yellow"], True)
        for button in self.buttons:
            button.draw(surface, fonts["small"], colors)
