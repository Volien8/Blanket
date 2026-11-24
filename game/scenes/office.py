import pygame

from ..scene import Scene
from ..ui import Button, bar, panel, text


class OfficeScene(Scene):
    ZONES = [
        ("BE", (35, 125, 210, 140), "teamlead_be"),
        ("FE-1 / FE-2", (260, 125, 250, 140), "teamlead_be"),
        ("QA", (540, 125, 210, 140), "teamlead_qa"),
        ("Документация", (780, 125, 210, 140), "teamlead_qa"),
        ("Внедрение", (1020, 125, 225, 140), "customer"),
        ("Поддержка", (35, 305, 210, 140), "support"),
        ("Продажи", (260, 305, 210, 140), "sales"),
        ("CEO", (485, 305, 210, 140), "ceo"),
        ("Бухгалтерия", (710, 305, 210, 140), "accounting"),
        ("Легаси-монолит", (935, 305, 310, 140), "legacy"),
    ]

    def __init__(self, game):
        super().__init__(game)
        self.hover = None
        self.log_open = False
        self.buttons = [
            Button((35, 635, 175, 45), "Синхронизация", self.open_sync),
            Button((225, 635, 145, 45), "Релиз", self.open_release),
            Button((385, 635, 145, 45), "Легаси", self.open_legacy),
            Button((545, 635, 180, 45), "Завершить день", self.next_day),
            Button((740, 635, 145, 45), "Сохранить", self.save),
            Button((900, 635, 145, 45), "Журнал", self.toggle_log),
        ]

    def open_sync(self):
        from .sync import SyncScene
        self.game.change_scene(SyncScene(self.game))

    def open_release(self):
        from .release import ReleaseScene
        self.game.change_scene(ReleaseScene(self.game))

    def open_legacy(self):
        from .legacy import LegacyScene
        self.game.change_scene(LegacyScene(self.game))

    def open_dialog(self, key):
        from .dialog import DialogScene
        self.game.change_scene(DialogScene(self.game, key))

    def save(self):
        self.game.save()

    def toggle_log(self):
        self.log_open = not self.log_open

    def next_day(self):
        from .end import EndScene
        state = self.game.state
        self.game.end_round()
        if state.budget <= 0:
            self.game.change_scene(EndScene(self.game, "Поражение", "Бухгалтерия забрала бюджет."))
        elif state.round > self.game.config["game"]["max_rounds"]:
            self.game.change_scene(EndScene(self.game, "Поражение", "Раунды закончились, а релиз всё ещё в лифте."))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.MOUSEMOTION:
            self.hover = next((key for name, rect, key in self.ZONES if pygame.Rect(rect).collidepoint(event.pos)), None)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for _, rect, key in self.ZONES:
                if pygame.Rect(rect).collidepoint(event.pos):
                    if key == "legacy":
                        self.open_legacy()
                    elif key in {"teamlead_be", "teamlead_qa", "ceo"}:
                        self.open_dialog(key)
                    elif key == "customer":
                        self.game.state.customers[1].satisfaction = max(0, self.game.state.customers[1].satisfaction - 2)
                        self.game.state.add_log("Заказчик Legal напомнил про договор и юриста.")
                    else:
                        self.game.state.add_log(f"Вы осмотрели зону «{_}».")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from .menu import MenuScene
            self.game.change_scene(MenuScene(self.game))

    def draw(self, surface):
        colors, fonts, state = self.game.colors, self.game.fonts, self.game.state
        surface.fill(colors["bg"])
        panel(surface, pygame.Rect(0, 0, 1280, 90), colors)
        text(surface, f"ДЕНЬ {state.round}/15", (20, 15), fonts["heading"], colors["text"])
        metrics = [("⚡", state.energy, colors["yellow"]), ("Бумажки", state.papers, colors["yellow"]),
                   ("Бюджет", state.budget, colors["green"]), ("Карма CEO", state.karma, colors["purple"]),
                   ("Стресс", state.stress, colors["red"])]
        for i, (name, value, color) in enumerate(metrics):
            text(surface, f"{name}: {value}", (20 + i * 150, 57), fonts["small"], color)
        text(surface, "OPEN SPACE / проект «Одеяло»", (1060, 25), fonts["small"], colors["muted"], True)
        for name, rect, key in self.ZONES:
            box = pygame.Rect(rect)
            fill = colors["panel_light"] if key == self.hover else colors["panel"]
            panel(surface, box, colors, fill)
            text(surface, name, box.center, fonts["body"], colors["text"], True)
            if key == "legacy":
                legacy = state.legacy
                text(surface, f"{legacy.status} / каскад {legacy.cascade}", (box.centerx, box.bottom - 28), fonts["small"], colors["red"], True)
            elif key == "customer":
                text(surface, "4 заказчика", (box.centerx, box.bottom - 28), fonts["small"], colors["muted"], True)
        for button in self.buttons:
            button.draw(surface, fonts["small"], colors)
        if self.log_open:
            panel(surface, pygame.Rect(790, 100, 460, 500), colors)
            text(surface, "ЖУРНАЛ СОБЫТИЙ", (1020, 125), fonts["heading"], colors["accent"], True)
            for index, line in enumerate(state.log[-18:]):
                text(surface, line, (810, 160 + index * 23), fonts["small"], colors["muted"])
