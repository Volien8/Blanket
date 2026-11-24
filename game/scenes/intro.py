import pygame

from ..branding import AUTHOR_SIGNATURE, GAME_TITLE
from ..people import draw_portrait
from ..scene import Scene
from ..ui import Button, panel, text


class IntroScene(Scene):
    """Преамбула, объясняющая роль игрока и условия победы."""

    def __init__(self, game):
        super().__init__(game)
        self.game.audio.speak("Вступление. Десять рабочих дней до релиза.")
        self.begin = Button((830, 575, 300, 55), "Начать рабочий день", self.start)

    def start(self):
        self.game.audio.play("success")
        from .office import OfficeScene
        self.game.state.add_log("РП вошёл в офис. Одеяло уже тянется к выходу.")
        self.game.change_scene(OfficeScene(self.game))

    def handle_event(self, event):
        self.begin.handle(event)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.start()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from .menu import MenuScene
            self.game.change_scene(MenuScene(self.game))

    def draw(self, surface):
        colors, fonts = self.game.colors, self.game.fonts
        surface.fill(colors["bg"])
        text(surface, GAME_TITLE, (640, 62), fonts["title"], colors["accent"], True)
        text(surface, "ПРЕАМБУЛА", (640, 115), fonts["heading"], colors["pink"], True)
        panel(surface, pygame.Rect(80, 155, 1120, 380), colors, (29, 38, 65))
        draw_portrait(surface, (210, 330), 1.45, "manager", colors, "stern")
        text(surface, "Вы — руководитель проекта.", (390, 205), fonts["heading"], colors["text"], max_width=730)
        max_rounds = self.game.config["game"]["max_rounds"]
        text(surface, f"Ваша задача — провести флагманский релиз через {max_rounds} рабочих дней.",
             (390, 270), fonts["body"], colors["muted"], max_width=720)
        text(surface, "Пять команд делят один ресурс, QA требует время, заказчики требуют всё сразу, а бухгалтерия уже приготовила печать.",
             (390, 325), fonts["body"], colors["muted"], max_width=720)
        text(surface, "Победа: релиз отправлен, команды готовы, бюджет не ушёл в долг, Legacy погашен.",
             (390, 405), fonts["body"], colors["green"], max_width=720)
        text(surface, "Поражение: бюджет исчез, раунды закончились или релиз ушёл с критическими проблемами.",
             (390, 455), fonts["body"], colors["red"], max_width=720)
        text(surface, AUTHOR_SIGNATURE, (80, 675), fonts["small"], colors["muted"])
        self.begin.draw(surface, fonts["body"], colors)
