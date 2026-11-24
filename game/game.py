import json
import random
from pathlib import Path
import pygame

from .entities import GameState
from .scenes.menu import MenuScene


ROOT = Path(__file__).resolve().parent.parent


class Game:
    def __init__(self):
        with (ROOT / "data" / "config.json").open(encoding="utf-8") as source:
            self.config = json.load(source)
        window = self.config["window"]
        pygame.init()
        self.screen = pygame.display.set_mode((window["width"], window["height"]))
        self.canvas = pygame.Surface((1280, 720))
        pygame.display.set_caption("ОДЕЯЛО — офисный квест")
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.SysFont("arial", 46, bold=True),
            "heading": pygame.font.SysFont("arial", 28, bold=True),
            "body": pygame.font.SysFont("arial", 20),
            "small": pygame.font.SysFont("arial", 16),
        }
        self.colors = {
            "bg": (25, 29, 38), "panel": (42, 49, 63), "panel_light": (62, 73, 91),
            "text": (235, 239, 245), "muted": (157, 168, 183), "accent": (76, 156, 216),
            "green": (92, 196, 123), "red": (224, 92, 98), "yellow": (236, 194, 76),
            "purple": (190, 124, 218), "border": (105, 119, 140)
        }
        self.state = GameState.new(self.config["game"])
        self.scene = MenuScene(self)
        self.running = True

    def change_scene(self, scene):
        self.scene = scene

    def new_state(self):
        self.state = GameState.new(self.config["game"])

    def save(self):
        path = ROOT / "save" / "slot1.json"
        path.parent.mkdir(exist_ok=True)
        with path.open("w", encoding="utf-8") as target:
            json.dump(self.state.to_dict(), target, ensure_ascii=False, indent=2)
        self.state.add_log("Сохранение записано в слот «Последняя надежда».")

    def load(self):
        path = ROOT / "save" / "slot1.json"
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
            state.budget = max(0, state.budget - 10)
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
        if state.legacy.status == "replacing" and state.legacy.cascade:
            state.legacy.cascade += 1
            state.add_log("Легаси породил ещё одну ошибку в каскаде.")
        state.energy = 5
        state.round += 1

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    if hasattr(event, "pos") and event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                        scale_x = self.canvas.get_width() / self.screen.get_width()
                        scale_y = self.canvas.get_height() / self.screen.get_height()
                        event = pygame.event.Event(event.type, {**event.dict, "pos": (int(event.pos[0] * scale_x), int(event.pos[1] * scale_y))})
                    self.scene.handle_event(event)
            self.scene.update()
            self.scene.draw(self.canvas)
            pygame.transform.smoothscale(self.canvas, self.screen.get_size(), self.screen)
            pygame.display.flip()
            self.clock.tick(self.config["window"]["fps"])
        pygame.quit()
