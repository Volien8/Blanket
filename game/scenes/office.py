import pygame

from ..people import draw_avatar, draw_person
from ..scene import Scene
from ..ui import Button, bar, panel, text, tooltip


class OfficeScene(Scene):
    ZONES = [
        ("BE", (35, 125, 210, 140), "teamlead_be", "be", "Бэкенд: поговорить с тимлидом и перераспределить ресурс."),
        ("FE-1 / FE-2", (260, 125, 250, 140), "teamlead_fe", "fe", "Фронтенд: проверить готовность двух команд."),
        ("QA", (540, 125, 210, 140), "teamlead_qa", "qa", "QA: ручные проверки, автотесты и риск релиза."),
        ("Документация", (780, 125, 210, 140), "docs", "docs", "Документация: готовность инструкций для заказчиков."),
        ("Внедрение", (1020, 125, 225, 140), "customer", "customer", "Четыре заказчика: понимание, юридическое давление и терпение."),
        ("Поддержка", (35, 305, 210, 140), "support", "support", "Техподдержка: бумажки, эскалации и звёздный сотрудник."),
        ("Продажи", (260, 305, 210, 140), "sales", "sales", "Продажи: обещания клиентам и неожиданные сюрпризы."),
        ("CEO", (485, 305, 210, 140), "ceo", "ceo", "Гендиректор: закупки, повышения и карма."),
        ("Бухгалтерия", (710, 305, 160, 140), "accounting", "accounting", "Бухгалтерия: штрафы, долг и печать «ШТРАФ»."),
        ("Legacy-монолит", (935, 305, 310, 140), "legacy", "legacy", "Legacy-монолит — старый связанный модуль, который трудно менять. Анализ снижает непрозрачность и тратит энергию; подмена может вызвать каскад ошибок; стабилизация гасит ошибки за бюджет. Для полной победы Legacy нужно заменить и погасить каскад."),
    ]

    def __init__(self, game):
        super().__init__(game)
        self.hover = None
        self.selected_index = 0
        self.log_open = False
        self.buttons = [
            Button((35, 635, 175, 45), "Синхронизация", self.open_sync, tooltip="Сравнить ответы трёх команд."),
            Button((225, 635, 145, 45), "Релиз", self.open_release, tooltip="Проверить готовность и отправить релиз."),
            Button((385, 635, 145, 45), "Legacy", self.open_legacy, tooltip="Открыть экран ремонта монолита."),
            Button((545, 635, 180, 45), "Завершить день", self.next_day, tooltip="Продвинуться на следующий день."),
            Button((740, 635, 145, 45), "Сохранить", self.save, tooltip="Записать состояние в слот."),
            Button((900, 635, 145, 45), "Журнал", self.toggle_log, tooltip="Показать последние события."),
            Button((1090, 635, 55, 45), "←", self.previous_zone, tooltip="Предыдущая зона (клавиша ←)."),
            Button((1155, 635, 55, 45), "→", self.next_zone, tooltip="Следующая зона (клавиша →)."),
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

    def previous_zone(self):
        self.selected_index = (self.selected_index - 1) % len(self.ZONES)

    def next_zone(self):
        self.selected_index = (self.selected_index + 1) % len(self.ZONES)

    def activate_selected(self):
        _, _, key, _, _ = self.ZONES[self.selected_index]
        if key == "legacy":
            self.open_legacy()
        elif key in {"teamlead_be", "teamlead_fe", "teamlead_qa", "docs", "customer", "support", "sales", "ceo", "accounting"}:
            self.open_dialog(key)

    def next_day(self):
        from .end import EndScene
        state = self.game.state
        self.game.end_round()
        if state.budget <= 0:
            self.game.change_scene(EndScene(self.game, "ПОРАЖЕНИЕ", "Бухгалтерия забрала бюджет."))
        elif state.round > self.game.config["game"]["max_rounds"]:
            self.game.change_scene(EndScene(self.game, "ПОРАЖЕНИЕ", "Раунды закончились, а релиз всё ещё в лифте."))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.MOUSEMOTION:
            self.hover = next((index for index, (_, rect, *_rest) in enumerate(self.ZONES) if pygame.Rect(rect).collidepoint(event.pos)), None)
            if self.hover is not None:
                self.selected_index = self.hover
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, (_, rect, *_rest) in enumerate(self.ZONES):
                if pygame.Rect(rect).collidepoint(event.pos):
                    self.selected_index = index
                    self.activate_selected()
                    break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.previous_zone()
            elif event.key == pygame.K_RIGHT:
                self.next_zone()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.activate_selected()
            elif event.key == pygame.K_ESCAPE:
                from .menu import MenuScene
                self.game.change_scene(MenuScene(self.game))

    def draw(self, surface):
        colors, fonts, state = self.game.colors, self.game.fonts, self.game.state
        surface.fill(colors["bg"])
        panel(surface, pygame.Rect(0, 0, 1280, 90), colors)
        text(surface, f"ДЕНЬ {state.round}/15", (180, 15), fonts["heading"], colors["text"])
        metrics = [("Энергия", state.energy, colors["yellow"]), ("Бумажки", state.papers, colors["yellow"]),
                   ("Бюджет", state.budget, colors["green"]), ("Карма CEO", state.karma, colors["purple"]),
                   ("Стресс", state.stress, colors["red"])]
        for i, (name, value, color) in enumerate(metrics):
            text(surface, f"{name}: {value}", (180 + i * 150, 57), fonts["small"], color)
        text(surface, "ОФИС / проект «Одеяло»", (1060, 25), fonts["small"], colors["muted"], True)
        for index, (name, rect, key, role, hint) in enumerate(self.ZONES):
            box = pygame.Rect(rect)
            selected = index == self.selected_index
            fill = colors["panel_light"] if selected else colors["panel"]
            panel(surface, box, colors, fill)
            avatar_rect = pygame.Rect(box.centerx - 30, box.centery - 25, 60, 50) if key == "legacy" else pygame.Rect(box.centerx - 42, box.centery - 2, 84, 76)
            if not draw_avatar(surface, avatar_rect, role, colors, selected):
                draw_person(surface, (box.centerx, box.centery + 8), 0.8, role, colors, selected)
            text(surface, name, (box.centerx, box.top + 20), fonts["small"], colors["text"], True, max_width=box.width - 20)
            if key == "legacy":
                legacy = state.legacy
                text(surface, f"{legacy.status} / каскад {legacy.cascade}", (box.centerx, box.bottom - 18), fonts["small"], colors["red"], True, max_width=box.width - 20)
            elif key == "customer":
                text(surface, "4 заказчика", (box.centerx, box.bottom - 18), fonts["small"], colors["muted"], True)
        for button in self.buttons:
            button.draw(surface, fonts["small"], colors)
        active_button = next((button for button in self.buttons if button.hover and button.tooltip), None)
        if active_button:
            tooltip(surface, active_button.tooltip, (active_button.rect.x, active_button.rect.y - 72), fonts["small"], colors)
        elif self.hover is not None:
            tooltip(surface, self.ZONES[self.hover][4], (pygame.Rect(self.ZONES[self.hover][1]).x, 470), fonts["small"], colors)
        else:
            tooltip(surface, "Стрелки ←/→ выбирают зону, Enter открывает её. Наведите мышь для подсказки.", (35, 490), fonts["small"], colors, 430)
        if self.log_open:
            panel(surface, pygame.Rect(790, 100, 460, 500), colors)
            text(surface, "ЖУРНАЛ СОБЫТИЙ", (1020, 125), fonts["heading"], colors["accent"], True)
            for index, line in enumerate(state.log[-18:]):
                text(surface, line, (810, 160 + index * 23), fonts["small"], colors["muted"], max_width=420)
