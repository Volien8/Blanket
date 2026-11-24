import json
from pathlib import Path
import pygame

from ..people import draw_portrait
from ..scene import Scene
from ..ui import Button, panel, text, wrap_text


class DialogScene(Scene):
    def __init__(self, game, key):
        super().__init__(game)
        self.key = key
        data_path = Path(__file__).resolve().parents[2] / "data" / "dialogs.json"
        with data_path.open(encoding="utf-8") as source:
            self.dialogs = json.load(source)
        self.dialog = self.dialogs[key]
        if key == "ceo":
            self.dialog = dict(self.dialog)
            self.dialog["text"] = (
                "Главное — разработать 10% софта и уже заявлять о нём как о готовом продукте. "
                "Потом как-нибудь выкрутимся — лишь бы купили."
            )
            self.dialog["options"] = list(self.dialog["options"]) + [
                {"text": "Продать продукт как готовый", "action": "ceo_sell_buggy"}
            ]
        self.dialog["options"] = list(self.dialog["options"]) + [
            {"text": "Отмена", "action": "cancel"}
        ]
        self.message = ""
        button_width = 230 if len(self.dialog["options"]) == 5 else 270
        gap = 15
        total_width = len(self.dialog["options"]) * button_width + (len(self.dialog["options"]) - 1) * gap
        start_x = (1280 - total_width) // 2
        self.buttons = [
            Button((start_x + i * (button_width + gap), 585, button_width, 54), option["text"], lambda o=option: self.choose(o))
            for i, option in enumerate(self.dialog["options"])
        ]

    def choose(self, option):
        state = self.game.state
        action = option["action"]
        if action == "cancel":
            self.back()
            return
        effects = {
            "give_resource": lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[0], "readiness", min(100, state.teams[0].readiness + 15)), setattr(state, "karma", min(100, state.karma + 3)), "Ресурс отдан BE. FE уже смотрит неодобрительно."),
            "deny_resource": lambda: (setattr(state, "stress", state.stress + 5), setattr(state.teams[0], "suspicion", min(100, state.teams[0].suspicion + 10)), "BE получил отказ и записал это в блокнот."),
            "intervene": lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[0], "readiness", min(100, state.teams[0].readiness + 8)), "РП взял задачу себе. Тимлид сделал вид, что не обиделся."),
            "manual_qa": lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[3], "readiness", min(100, state.teams[3].readiness + 18)), "Ручная проверка нашла баг. Это хороший знак."),
            "pressure_qa": lambda: (setattr(state, "stress", state.stress + 4), setattr(state.teams[3], "suspicion", min(100, state.teams[3].suspicion + 15)), "QA пообещал ускориться. Очень угрожающе."),
            "trust_qa": lambda: (setattr(state.teams[3], "readiness", min(100, state.teams[3].readiness + 4)), "РП поверил зелёному отчёту."),
            "ceo_buy": lambda: (setattr(state, "papers", max(0, state.papers - 1)), setattr(state, "budget", min(100, state.budget + 15)), setattr(state, "karma", min(100, state.karma + 5)), "CEO подписала закупку. Бумажка победила."),
            "ceo_wait": lambda: (setattr(state, "stress", state.stress + 3), "CEO попросила прийти завтра. Классика."),
            "ceo_escalate": lambda: (setattr(state, "karma", max(0, state.karma - 4)), "CEO взяла юридическое давление на себя."),
            "ceo_sell_buggy": lambda: (setattr(state, "stress", state.stress + 10), setattr(state, "karma", min(100, state.karma + 2)), "CEO объявила продукт готовым и отправила его продавать, несмотря на баги."),
            "give_fe_time": lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[1], "readiness", min(100, state.teams[1].readiness + 14)), "FE получил время и перестал смотреть на BE.") ,
            "check_fe_api": lambda: (setattr(state, "stress", state.stress + 2), setattr(state.teams[1], "readiness", min(100, state.teams[1].readiness + 8)), "API проверен. Нашлась одна маленькая катастрофа."),
            "trust_fe": lambda: (setattr(state.teams[1], "readiness", min(100, state.teams[1].readiness + 4)), "РП поверил фронтенду на слово."),
            "give_docs_time": lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[4], "readiness", min(100, state.teams[4].readiness + 14)), "Документация получила время и открыла файл."),
            "ask_docs_draft": lambda: (setattr(state.teams[4], "readiness", min(100, state.teams[4].readiness + 8)), "Черновик найден. В нём больше вопросов, чем страниц."),
            "trust_docs": lambda: (setattr(state.teams[4], "readiness", min(100, state.teams[4].readiness + 3)), "Документация отправлена как есть."),
            "customer_escalate": lambda: (setattr(state, "karma", max(0, state.karma - 3)), setattr(state.customers[1], "satisfaction", min(100, state.customers[1].satisfaction + 8)), "CEO подключилась к разговору с юристом."),
            "customer_crutch": lambda: (setattr(state, "budget", max(0, state.budget - 5)), setattr(state.customers[1], "satisfaction", min(100, state.customers[1].satisfaction + 5)), "Костыль приклеен. Держится на честном слове."),
            "customer_explain": lambda: (setattr(state, "stress", state.stress + 3), "Заказчику объяснили порядок. Он записал номер юриста."),
            "support_paper": lambda: (setattr(state, "papers", max(0, state.papers - 1)), setattr(state.teams[5], "readiness", min(100, state.teams[5].readiness + 10)), "Бумажка выдана. Поддержка зашевелилась."),
            "support_star": lambda: (setattr(state, "energy", max(0, state.energy - 1)), setattr(state.teams[5], "readiness", min(100, state.teams[5].readiness + 15)), "Звёздный сотрудник решил вопрос за пять минут."),
            "support_escalate": lambda: (setattr(state, "karma", max(0, state.karma - 2)), "Заявка поднялась на самый верх папки."),
            "sales_task": lambda: (setattr(state, "stress", state.stress + 4), setattr(state.teams[6], "readiness", min(100, state.teams[6].readiness + 5)), "Мобильное приложение записано отдельной задачей."),
            "sales_cancel": lambda: (setattr(state, "karma", max(0, state.karma - 3)), "Продажи обещали больше ничего не обещать."),
            "sales_bluff": lambda: (setattr(state, "stress", state.stress + 7), "Все сделали вид, что мобильное приложение было в плане."),
            "accounting_sign": lambda: (setattr(state, "papers", max(0, state.papers - 1)), setattr(state, "budget", min(100, state.budget + 5)), "Акт подписан. Печать разочарована."),
            "accounting_pay": lambda: (setattr(state, "budget", max(0, state.budget - 15)), "Штраф оплачен. Бухгалтерия улыбается."),
            "accounting_wait": lambda: (setattr(state, "stress", state.stress + 5), "Отсрочка согласована до следующего звонка."),
        }
        result = effects[action]()
        self.message = result[-1]
        if self.key not in state.talked_to_today:
            state.talked_to_today.append(self.key)
        state.add_log(self.message)

    def back(self):
        from .office import OfficeScene
        self.game.change_scene(OfficeScene(self.game))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()

    def draw_bubble(self, surface, rect, message, font, colors):
        pygame.draw.ellipse(surface, (255, 255, 255), rect)
        pygame.draw.ellipse(surface, colors["accent"], rect, 3)
        tail = [(rect.left + 35, rect.bottom - 3), (rect.left + 12, rect.bottom + 28), (rect.left + 75, rect.bottom - 8)]
        pygame.draw.polygon(surface, (255, 255, 255), tail)
        pygame.draw.lines(surface, colors["accent"], True, tail, 3)
        lines = wrap_text(message, font, rect.width - 54)
        line_height = font.get_linesize()
        total = len(lines) * line_height
        for index, line in enumerate(lines):
            rendered = font.render(line, True, colors["panel"])
            surface.blit(rendered, rendered.get_rect(center=(rect.centerx, rect.centery - total // 2 + index * line_height + line_height // 2)))

    def draw(self, surface):
        colors, fonts = self.game.colors, self.game.fonts
        surface.fill(colors["bg"])
        panel(surface, pygame.Rect(55, 55, 1170, 500), colors, (30, 39, 68))
        draw_portrait(surface, (215, 340), 1.65, self.dialog["portrait"].lower(), colors, "neutral")
        text(surface, self.dialog["speaker"], (215, 490), fonts["heading"], colors["text"], True)
        current_text = self.message or self.dialog["text"]
        self.draw_bubble(surface, pygame.Rect(385, 130, 755, 205), current_text, fonts["body"], colors)
        text(surface, "Выберите ответ", (760, 465), fonts["heading"], colors["pink"], True)
        for button in self.buttons:
            button.draw(surface, fonts["small"], colors)
        text(surface, "Esc — назад", (30, 25), fonts["small"], colors["muted"])
