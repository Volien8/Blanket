import json
import pygame

from ..scene import Scene
from ..people import draw_person
from ..ui import Button, panel, text


class DialogScene(Scene):
    def __init__(self, game, key):
        super().__init__(game)
        with (game.__class__.__module__ and (game.__class__.__dict__.get('ROOT') or __import__('pathlib').Path(__file__).resolve().parents[2]) / 'data' / 'dialogs.json').open(encoding='utf-8') as source:
            self.dialogs = json.load(source)
        self.dialog = self.dialogs[key]
        self.message = ""
        self.buttons = [Button((150 + i * 330, 545, 300, 52), option["text"], lambda o=option: self.choose(o)) for i, option in enumerate(self.dialog["options"])]

    def choose(self, option):
        state = self.game.state
        action = option["action"]
        effects = {
            "give_resource": (lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[0], "readiness", min(100, state.teams[0].readiness + 15)), setattr(state, "karma", min(100, state.karma + 3)), "Ресурс отдан BE. FE уже смотрит неодобрительно.")),
            "deny_resource": (lambda: (setattr(state, "stress", state.stress + 5), setattr(state.teams[0], "suspicion", min(100, state.teams[0].suspicion + 10)), "BE получил отказ и записал это в блокнот.")),
            "intervene": (lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[0], "readiness", min(100, state.teams[0].readiness + 8)), "РП взял задачу себе. Тимлид сделал вид, что не обиделся.")),
            "manual_qa": (lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[3], "readiness", min(100, state.teams[3].readiness + 18)), "Ручная проверка нашла баг. Это хороший знак.")),
            "pressure_qa": (lambda: (setattr(state, "stress", state.stress + 4), setattr(state.teams[3], "suspicion", min(100, state.teams[3].suspicion + 15)), "QA пообещал ускориться. Очень угрожающе.")),
            "trust_qa": (lambda: (setattr(state.teams[3], "readiness", min(100, state.teams[3].readiness + 4)), "РП поверил зелёному отчёту.")),
            "ceo_buy": (lambda: (setattr(state, "papers", max(0, state.papers - 1)), setattr(state, "budget", min(100, state.budget + 15)), setattr(state, "karma", min(100, state.karma + 5)), "CEO подписала закупку. Бумажка победила.")),
            "ceo_wait": (lambda: (setattr(state, "stress", state.stress + 3), "CEO попросила прийти завтра. Классика.")),
            "ceo_escalate": (lambda: (setattr(state, "karma", max(0, state.karma - 4)), "CEO взяла юридическое давление на себя.")),
        }
        result = effects[action]()
        self.message = result[-1] if isinstance(result, tuple) else result
        state.add_log(self.message)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()

    def back(self):
        from .office import OfficeScene
        self.game.change_scene(OfficeScene(self.game))

    def draw(self, surface):
        colors, fonts = self.game.colors, self.game.fonts
        surface.fill(colors["bg"])
        panel(surface, pygame.Rect(80, 90, 1120, 410), colors)
        draw_person(surface, (250, 285), 2.0, self.dialog["portrait"].lower(), colors, True)
        text(surface, self.dialog["speaker"], (250, 430), fonts["heading"], colors["text"], True)
        text(surface, self.dialog["text"], (430, 180), fonts["heading"], colors["text"])
        if self.message:
            text(surface, self.message, (430, 260), fonts["body"], colors["yellow"])
        else:
            text(surface, "Выберите ответ:", (430, 260), fonts["body"], colors["muted"])
        for button in self.buttons:
            button.draw(surface, fonts["small"], colors)
        text(surface, "Esc — назад", (30, 30), fonts["small"], colors["muted"])
