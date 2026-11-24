import pygame

from ..scene import Scene
from ..ui import Button, bar, panel, text


class ReleaseScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.message = ""
        self.buttons = [
            Button((180, 610, 270, 50), "Отправить полностью", self.send_full),
            Button((505, 610, 270, 50), "Отправить без QA", self.send_risky),
            Button((830, 610, 270, 50), "Отмена", self.back),
        ]

    def send_full(self):
        state = self.game.state
        ready = all(team.readiness >= 70 for team in state.teams[:5])
        legacy_ok = state.legacy.status == "replaced" and state.legacy.cascade <= 3
        if ready and legacy_ok and state.budget > 0:
            state.release_sent = True
            state.release_mode = "full"
            state.add_log("Релиз утверждён и отправлен полностью.")
            from .end import EndScene
            self.game.change_scene(EndScene(self.game, "ПОБЕДА", "Одеяло поймано. Даже бухгалтерия признала результат."))
        else:
            self.message = "Не все группы готовы, либо легаси всё ещё шипит."

    def send_risky(self):
        state = self.game.state
        state.release_sent = True
        state.release_mode = "without_qa"
        state.stress += 15
        state.add_log("Релиз отправлен без QA. Это было смело. И неправильно.")
        from .end import EndScene
        self.game.change_scene(EndScene(self.game, "СЕРЫЙ ИСХОД", "Релиз собран, но QA подозрительно молчит."))

    def back(self):
        from .office import OfficeScene
        self.game.change_scene(OfficeScene(self.game))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()

    def draw(self, surface):
        colors, fonts, state = self.game.colors, self.game.fonts, self.game.state
        surface.fill(colors["bg"])
        text(surface, "ЭКРАН РЕЛИЗА", (640, 60), fonts["title"], colors["green"], True)
        text(surface, "Только РП решает, когда ракета взлетает.", (640, 110), fonts["body"], colors["muted"], True)
        for index, team in enumerate(state.teams[:5]):
            y = 165 + index * 68
            text(surface, team.name, (190, y), fonts["body"], colors["text"])
            bar(surface, pygame.Rect(370, y + 5, 500, 22), team.readiness, 100, colors["green"], colors)
            text(surface, f"{team.readiness}%", (895, y), fonts["body"], colors["text"])
        text(surface, f"Legacy: {state.legacy.status}, каскад {state.legacy.cascade}", (640, 530), fonts["body"], colors["red"], True)
        text(surface, self.message, (640, 575), fonts["small"], colors["yellow"], True)
        for button in self.buttons:
            button.draw(surface, fonts["small"], colors)
