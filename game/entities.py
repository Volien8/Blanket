from dataclasses import dataclass, field


@dataclass
class Team:
    name: str
    kind: str
    readiness: int
    honesty: int = 70
    suspicion: int = 0
    crutch_debt: int = 0


@dataclass
class Customer:
    name: str
    profile: str
    satisfaction: int = 65
    patience: int = 3
    legal_pressure: bool = False


@dataclass
class Legacy:
    status: str = "works"
    opacity: int = 80
    progress: int = 0
    cascade: int = 0


@dataclass
class GameState:
    round: int = 1
    energy: int = 5
    papers: int = 2
    budget: int = 100
    karma: int = 50
    stress: int = 0
    release_sent: bool = False
    release_mode: str | None = None
    talked_to_today: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    legacy: Legacy = field(default_factory=Legacy)
    teams: list[Team] = field(default_factory=list)
    customers: list[Customer] = field(default_factory=list)

    @classmethod
    def new(cls, config):
        groups = [
            Team("BE", "dev", 35, 78), Team("FE-1", "dev", 42, 62),
            Team("FE-2", "dev", 38, 58), Team("QA", "qa", 30, 72),
            Team("Документация", "docs", 25, 82), Team("Поддержка", "support", 45, 88),
            Team("Продажи", "sales", 50, 55)
        ]
        return cls(
            energy=config["starting_energy"], papers=config["starting_papers"],
            budget=config["starting_budget"], karma=config["starting_karma"],
            teams=groups,
            customers=[
                Customer("Understanding", "understanding", 75, 4),
                Customer("Legal", "legal", 55, 3, True),
                Customer("Nervous", "nervous", 60, 3),
                Customer("Indifferent", "indifferent", 50, 2)
            ]
        )

    def add_log(self, message):
        self.log.append(f"День {self.round}: {message}")
        del self.log[:-30]

    def to_dict(self):
        data = self.__dict__.copy()
        data["legacy"] = self.legacy.__dict__.copy()
        data["teams"] = [team.__dict__.copy() for team in self.teams]
        data["customers"] = [customer.__dict__.copy() for customer in self.customers]
        return data

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data["legacy"] = Legacy(**data.get("legacy", {}))
        data["teams"] = [Team(**team) for team in data.get("teams", [])]
        data["customers"] = [Customer(**customer) for customer in data.get("customers", [])]
        return cls(**data)
