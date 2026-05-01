import random
from dataclasses import dataclass, field
from typing import Literal

Team = Literal["mafia", "town"]

@dataclass
class Role:
    key: str
    name: str        # Uzbek name
    team: Team
    emoji: str

MAFIA   = Role("mafia",   "Mafiya",  "mafia", "🔴")
DOCTOR  = Role("doctor",  "Doktor",  "town",  "💚")
SHERIFF = Role("sheriff", "Sherif",  "town",  "🔵")
CITIZEN = Role("citizen", "Fuqaro",  "town",  "⚪")

@dataclass
class Player:
    user_id: int
    name: str
    role: Role = field(default=None)
    alive: bool = True
    has_acted: bool = False    # reset each night/vote
    self_save_used: bool = False  # doctor self-save limit


def assign_roles(players: list[Player]) -> None:
    n = len(players)
    mafia_count = max(1, n // 4)

    roles = (
        [MAFIA] * mafia_count
        + [DOCTOR]
        + [SHERIFF]
        + [CITIZEN] * (n - mafia_count - 2)
    )
    random.shuffle(roles)
    for player, role in zip(players, roles):
        player.role = role
