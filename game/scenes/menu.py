import pygame

from ..scene import Scene
from ..ui import Button, panel, text


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        cx = 640
        self.about = False
        self.buttons = [
            Button((cx - 150, 315, 300, 48), "Новая игра", self.new_game),
            Button((cx - 150, 375, 300, 48), "Продолжить", self.continue_game),
            Button((cx - 150, 435, 300, 48), "Об игре", self.toggle_about),
            Button((cx - 150, 495, 300, 48), "Выход", self.quit),
        ]

    def new_game(self):
        self.game.new_state()
        self.game.state.add_log("Одеяло снова убежало. Рабочий день начался.")
        from .office import OfficeScene
        self.game.change_scene(OfficeScene(self.game))

    def continue_game(self):
        if self.game.load():
            from .office import OfficeScene
            self.game.change_scene(OfficeScene(self.game))
        else:
            self.about = True

    def toggle_about(self):
        self.about = not self.about

    def quit(self):
        self.game.running = False

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit()

    def draw(self, surface):
        colors, fonts = self.game.colors, self.game.fonts
        surface.fill(colors["bg"])
        text(surface, "ОДЕЯЛО", (640, 110), fonts["title"], colors["accent"], True)
        text(surface, "графический квест о дедлайнах, легаси и корпоративной дипломатии",
             (640, 170), fonts["body"], colors["muted"], True)
        poem = ["Одеяло убежало, тимлид в шоке — не догнал.",
                "Пять команд его тянули, а ресурс — один. Пропал.",
                "Релиз ждут уже вчера. Бухгалтерия — всегда."]
        for index, line in enumerate(poem):
            text(surface, line, (640, 220 + index * 24), fonts["small"], colors["muted"], True)
        for button in self.buttons:
            button.draw(surface, fonts["body"], colors)
        if self.about:
            panel(surface, pygame.Rect(390, 570, 500, 100), colors)
            text(surface, "Поймайте одеяло, переживите 15 дней и отправьте",
                 (640, 595), fonts["small"], colors["text"], True)
            text(surface, "релиз без критических багов и долгов.",
                 (640, 622), fonts["small"], colors["yellow"], True)
