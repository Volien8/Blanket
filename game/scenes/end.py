import pygame

from ..scene import Scene
from ..ui import Button, gradient_background, text


class EndScene(Scene):
    def __init__(self, game, title, reason):
        super().__init__(game)
        self.game.audio.speak(f"{title}. {reason}")
        self.title, self.reason = title, reason
        self.buttons = [Button((380, 500, 240, 52), "Заново", self.restart), Button((660, 500, 240, 52), "В меню", self.menu)]

    def restart(self):
        from .office import OfficeScene
        self.game.new_state()
        self.game.change_scene(OfficeScene(self.game))

    def menu(self):
        from .menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)

    def draw(self, surface):
        colors, fonts = self.game.colors, self.game.fonts
        gradient_background(surface, colors)
        color = colors["green"] if self.title == "ПОБЕДА" else colors["yellow"] if self.title == "СЕРЫЙ ИСХОД" else colors["red"]
        text(surface, self.title, (640, 220), fonts["title"], color, True)
        text(surface, self.reason, (640, 315), fonts["heading"], colors["text"], True)
        text(surface, "Спасибо, что не отправили всё в пятницу вечером.", (640, 370), fonts["body"], colors["muted"], True)
        for button in self.buttons:
            button.draw(surface, fonts["body"], colors)
