import pygame
from pathlib import Path

from ..branding import AUTHOR_NAME, AUTHOR_SIGNATURE, GAME_TITLE
from ..scene import Scene
from ..ui import Button, gradient_background, panel, text, tooltip


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.about = False
        self.selected_slot = 1
        self.has_save = self.slot_exists()
        self.buttons = [
            Button((470, 285, 340, 52), "Новая игра", self.new_game, tooltip="Начать новую историю руководителя проекта."),
            Button((470, 350, 340, 52), "Продолжить", self.continue_game, tooltip="Загрузить выбранный слот." if self.has_save else "Сохранений в выбранном слоте пока нет.", enabled=self.has_save),
            Button((470, 415, 340, 52), "Об игре", self.toggle_about, tooltip="Посмотреть цель и правила игры."),
            Button((470, 480, 340, 52), "Выход", self.quit, tooltip="Закрыть игру."),
            Button((940, 65, 62, 34), "<", self.previous_slot, tooltip="Предыдущий слот сохранения."),
            Button((1100, 65, 62, 34), ">", self.next_slot, tooltip="Следующий слот сохранения."),
        ]

    def slot_exists(self):
        return (Path(__file__).resolve().parents[2] / "save" / f"slot{self.selected_slot}.json").exists()

    def update_slot_state(self):
        self.has_save = self.slot_exists()
        self.buttons[1].enabled = self.has_save
        self.game.active_slot = self.selected_slot

    def previous_slot(self):
        self.selected_slot = 3 if self.selected_slot == 1 else self.selected_slot - 1
        self.update_slot_state()

    def next_slot(self):
        self.selected_slot = 1 if self.selected_slot == 3 else self.selected_slot + 1
        self.update_slot_state()

    def new_game(self):
        self.game.active_slot = self.selected_slot
        self.game.new_state()
        from .intro import IntroScene
        self.game.change_scene(IntroScene(self.game))

    def continue_game(self):
        if self.has_save and self.game.load(self.selected_slot):
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
        gradient_background(surface, colors)
        text(surface, GAME_TITLE, (640, 78), fonts["title"], colors["accent"], True)
        text(surface, "Офисный квест о дедлайнах, командах и одном убежавшем одеяле",
             (640, 145), fonts["body"], colors["muted"], True, max_width=620)
        text(surface, "Выберите действие", (640, 225), fonts["heading"], colors["text"], True)
        text(surface, f"Слот сохранения: {self.selected_slot}", (1050, 83), fonts["small"], colors["muted"], True)
        for button in self.buttons:
            button.draw(surface, fonts["body"], colors)
        active_button = next((button for button in self.buttons if button.hover and button.tooltip), None)
        if active_button:
            tooltip(surface, active_button.tooltip, (active_button.rect.right + 18, active_button.rect.y), fonts["small"], colors)
        if self.about:
            panel(surface, pygame.Rect(390, 560, 500, 120), colors, colors["panel_light"])
            max_rounds = self.game.config["game"]["max_rounds"]
            text(surface, f"Цель: довести релиз до заказчиков за {max_rounds} дней.", (640, 585), fonts["small"], colors["text"], True, 460)
            text(surface, "Следите за бюджетом, кармой, стрессом и Legacy.", (640, 620), fonts["small"], colors["yellow"], True, 460)
            text(surface, f"Автор: {AUTHOR_NAME}", (640, 652), fonts["small"], colors["muted"], True)
        poem = [
            "Одеяло убежало, тимлид в шоке — не догнал.",
            "Пять команд его тянули, а ресурс — один. Пропал.",
            "Релиз ждут уже вчера. Бухгалтерия — всегда.",
        ]
        panel(surface, pygame.Rect(875, 505, 370, 160), colors, (26, 34, 59))
        text(surface, "Преамбула проекта", (1060, 530), fonts["small"], colors["pink"], True)
        for index, line in enumerate(poem):
            text(surface, line, (895, 555 + index * 22), fonts["small"], colors["muted"], max_width=330)
        text(surface, AUTHOR_SIGNATURE, (1060, 645), fonts["small"], colors["yellow"], True)
