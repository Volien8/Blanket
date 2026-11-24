import json
import random
from pathlib import Path
import pygame

from .entities import GameState
from .branding import AUTHOR_NAME, GAME_TITLE
from .audio import AudioManager
from .scenes.menu import MenuScene
from .ui import Button


ROOT = Path(__file__).resolve().parent.parent


class Game:
    def __init__(self):
        with (ROOT / "data" / "config.json").open(encoding="utf-8") as source:
            self.config = json.load(source)
        window = self.config["window"]
        pygame.init()
        self.screen = pygame.display.set_mode((window["width"], window["height"]))
        self.audio = AudioManager(ROOT)
        self.notifications = []
        self.transition_alpha = 0
        self.active_slot = 1
        self.canvas = pygame.Surface((1280, 720))
        self.author = AUTHOR_NAME
        pygame.display.set_caption(f"{GAME_TITLE} — офисный квест — {self.author}")
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.SysFont("arial", 46, bold=True),
            "heading": pygame.font.SysFont("arial", 28, bold=True),
            "body": pygame.font.SysFont("arial", 20),
            "small": pygame.font.SysFont("arial", 16),
        }
        self.colors = {
            "bg": (17, 22, 38), "panel": (34, 42, 68), "panel_light": (49, 61, 96),
            "text": (245, 248, 255), "muted": (170, 184, 211), "accent": (54, 174, 255),
            "green": (84, 224, 151), "red": (255, 103, 122), "yellow": (255, 211, 77),
            "purple": (219, 123, 255), "border": (102, 126, 178), "pink": (255, 103, 191)
        }
        self.state = GameState.new(self.config["game"])
        self.scene = MenuScene(self)
        self.back_button = Button((18, 12, 112, 32), "← Назад", self.back_to_previous, accent=(47, 82, 130), tooltip="Вернуться на предыдущий экран.")
        self.running = True

    def change_scene(self, scene):
        self.scene = scene
        self.transition_alpha = 210

    def new_state(self):
        self.state = GameState.new(self.config["game"])

    def back_to_previous(self):
        if hasattr(self.scene, "back"):
            self.scene.back()
        else:
            self.change_scene(MenuScene(self))

    def notify(self, message, color=None):
        self.notifications.append({"text": message, "until": pygame.time.get_ticks() + 2600, "color": color or self.colors["yellow"]})
        self.notifications = self.notifications[-4:]

    def save(self, slot=None):
        if slot is not None:
            self.active_slot = max(1, min(3, int(slot)))
        path = ROOT / "save" / f"slot{self.active_slot}.json"
        path.parent.mkdir(exist_ok=True)
        with path.open("w", encoding="utf-8") as target:
            json.dump(self.state.to_dict(), target, ensure_ascii=False, indent=2)
        self.state.add_log("Сохранение записано в слот «Последняя надежда».")

    def load(self, slot=None):
        if slot is not None:
            self.active_slot = max(1, min(3, int(slot)))
        path = ROOT / "save" / f"slot{self.active_slot}.json"
        if not path.exists():
            return False
        with path.open(encoding="utf-8") as source:
            self.state = GameState.from_dict(json.load(source))
        return True

    def end_round(self):
        state = self.state
        for team in state.teams:
            team.readiness = min(100, team.readiness + random.randint(3, 10))
        for customer in state.customers:
            customer.patience = max(0, customer.patience - 1)
        event = random.choice(["accounting", "sales", "customer", "support"])
        if event == "accounting":
            state.budget -= 10
            state.add_log("Бухгалтерия выписала штраф. Штамп поставлен с удовольствием.")
        elif event == "sales":
            state.stress += 8
            state.add_log("Продажи забыли сказать про мобильное приложение.")
        elif event == "customer":
            state.stress += 5
            state.customers[2].satisfaction = max(0, state.customers[2].satisfaction - 5)
            state.add_log("Нервный заказчик спросил, точно ли оно будет работать.")
        else:
            if state.papers:
                state.papers -= 1
                state.add_log("Звёздный сотрудник спас ситуацию за одну бумажку.")
            else:
                state.stress += 4
                state.add_log("Поддержка ждёт бумажку. Сервер тоже ждёт.")
        state.talked_to_today.clear()
        random.shuffle(state.office_order)
        if "ceo_sell_buggy" in state.decision_flags:
            state.stress += 3
            state.add_log("Проданный сырой продукт начал возвращаться с вопросами от клиентов.")
        if "sales_bluff" in state.decision_flags:
            state.budget -= 5
            state.add_log("Продажи прислали счёт за обещания, которых не было в плане.")
        if state.legacy.status == "replacing" and state.legacy.cascade:
            state.legacy.cascade += 1
            state.add_log("Legacy породил ещё одну ошибку в каскаде.")
        state.energy = 5
        state.round += 1

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    consumed = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.audio.play("click")
                    if not isinstance(self.scene, MenuScene):
                        self.back_button.handle(event)
                        consumed = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.back_button.rect.collidepoint(event.pos)
                    if hasattr(event, "pos") and event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                        scale_x = self.canvas.get_width() / self.screen.get_width()
                        scale_y = self.canvas.get_height() / self.screen.get_height()
                        event = pygame.event.Event(event.type, {**event.dict, "pos": (int(event.pos[0] * scale_x), int(event.pos[1] * scale_y))})
                    if not consumed:
                        self.scene.handle_event(event)
            self.scene.update()
            self.scene.draw(self.canvas)
            if not isinstance(self.scene, MenuScene):
                self.back_button.draw(self.canvas, self.fonts["small"], self.colors)
            now = pygame.time.get_ticks()
            self.notifications = [item for item in self.notifications if item["until"] > now]
            for index, item in enumerate(self.notifications):
                box = pygame.Rect(18, 58 + index * 42, 380, 34)
                pygame.draw.rect(self.canvas, (21, 25, 33), box, border_radius=8)
                pygame.draw.rect(self.canvas, item["color"], box, 2, border_radius=8)
                rendered = self.fonts["small"].render(item["text"], True, self.colors["text"])
                self.canvas.blit(rendered, rendered.get_rect(midleft=(box.left + 12, box.centery)))
            if self.transition_alpha > 0:
                overlay = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, self.transition_alpha))
                self.canvas.blit(overlay, (0, 0))
                self.transition_alpha = max(0, self.transition_alpha - 18)
            pygame.transform.smoothscale(self.canvas, self.screen.get_size(), self.screen)
            pygame.display.flip()
            self.clock.tick(self.config["window"]["fps"])
        pygame.quit()
