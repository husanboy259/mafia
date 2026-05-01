from __future__ import annotations
from typing import Literal, Optional
from roles import Player, Role, MAFIA, DOCTOR, SHERIFF, CITIZEN, assign_roles

State = Literal["lobby", "night", "day", "vote", "ended"]


class MafiaGame:
    def __init__(self, group_id: int, host_id: int, host_name: str):
        self.group_id = group_id
        self.host_id = host_id
        self.state: State = "lobby"
        self.players: dict[int, Player] = {}
        self.round: int = 0

        # night action targets
        self.mafia_target: Optional[int] = None   # user_id
        self.doctor_target: Optional[int] = None  # user_id
        self.sheriff_target: Optional[int] = None # user_id
        self.sheriff_result: Optional[str] = None

        # vote tallies  {voter_id: target_id or None(skip)}
        self.votes: dict[int, Optional[int]] = {}

        self.add_player(host_id, host_name)

    # ------------------------------------------------------------------
    # Lobby
    # ------------------------------------------------------------------
    def add_player(self, user_id: int, name: str) -> bool:
        if user_id in self.players:
            return False
        self.players[user_id] = Player(user_id=user_id, name=name)
        return True

    def player_count(self) -> int:
        return len(self.players)

    # ------------------------------------------------------------------
    # Start
    # ------------------------------------------------------------------
    def start(self) -> None:
        assign_roles(list(self.players.values()))
        self.state = "night"
        self.round = 1
        self._reset_night_actions()

    # ------------------------------------------------------------------
    # Night
    # ------------------------------------------------------------------
    def _reset_night_actions(self) -> None:
        self.mafia_target = None
        self.doctor_target = None
        self.sheriff_target = None
        self.sheriff_result = None
        for p in self.players.values():
            p.has_acted = False

    def alive_players(self) -> list[Player]:
        return [p for p in self.players.values() if p.alive]

    def alive_others(self, exclude_id: int) -> list[Player]:
        return [p for p in self.alive_players() if p.user_id != exclude_id]

    def mafia_players(self) -> list[Player]:
        return [p for p in self.players.values() if p.role == MAFIA and p.alive]

    def record_mafia_vote(self, voter_id: int, target_id: int) -> bool:
        player = self.players.get(voter_id)
        if not player or not player.alive or player.has_acted:
            return False
        self.mafia_target = target_id
        # mark all mafia as acted once anyone votes
        for mp in self.mafia_players():
            mp.has_acted = True
        return True

    def record_doctor_action(self, doctor_id: int, target_id: int) -> bool:
        player = self.players.get(doctor_id)
        if not player or not player.alive or player.has_acted:
            return False
        # prevent self-save twice
        if target_id == doctor_id and player.self_save_used:
            return False
        if target_id == doctor_id:
            player.self_save_used = True
        self.doctor_target = target_id
        player.has_acted = True
        return True

    def record_sheriff_action(self, sheriff_id: int, target_id: int) -> bool:
        player = self.players.get(sheriff_id)
        if not player or not player.alive or player.has_acted:
            return False
        target = self.players.get(target_id)
        if not target:
            return False
        self.sheriff_target = target_id
        self.sheriff_result = "mafia" if target.role == MAFIA else "clean"
        player.has_acted = True
        return True

    def all_night_actions_done(self) -> bool:
        mafia_done = all(mp.has_acted for mp in self.mafia_players())
        doctor = self._get_role_player(DOCTOR)
        sheriff = self._get_role_player(SHERIFF)
        doctor_done = (doctor is None or not doctor.alive or doctor.has_acted)
        sheriff_done = (sheriff is None or not sheriff.alive or sheriff.has_acted)
        return mafia_done and doctor_done and sheriff_done

    def _get_role_player(self, role: Role) -> Optional[Player]:
        for p in self.players.values():
            if p.role == role:
                return p
        return None

    def resolve_night(self) -> Optional[Player]:
        """Apply night actions. Returns killed player or None if saved."""
        killed: Optional[Player] = None
        if self.mafia_target is not None:
            if self.mafia_target != self.doctor_target:
                victim = self.players.get(self.mafia_target)
                if victim:
                    victim.alive = False
                    killed = victim
        self.state = "day"
        return killed

    # ------------------------------------------------------------------
    # Vote
    # ------------------------------------------------------------------
    def start_vote(self) -> None:
        self.state = "vote"
        self.votes = {}
        for p in self.alive_players():
            p.has_acted = False

    def record_vote(self, voter_id: int, target_id: Optional[int]) -> bool:
        player = self.players.get(voter_id)
        if not player or not player.alive or player.has_acted:
            return False
        self.votes[voter_id] = target_id
        player.has_acted = True
        return True

    def all_voted(self) -> bool:
        return all(p.has_acted for p in self.alive_players())

    def resolve_vote(self) -> Optional[Player]:
        """Eliminate player with most votes. Returns eliminated player or None."""
        tally: dict[Optional[int], int] = {}
        for target in self.votes.values():
            tally[target] = tally.get(target, 0) + 1

        if not tally:
            self._next_night()
            return None

        max_votes = max(tally.values())
        top = [t for t, v in tally.items() if v == max_votes and t is not None]

        if len(top) != 1:  # tie or all skipped
            self._next_night()
            return None

        eliminated = self.players.get(top[0])
        if eliminated:
            eliminated.alive = False
        self._next_night()
        return eliminated

    def _next_night(self) -> None:
        self.state = "night"
        self.round += 1
        self._reset_night_actions()

    # ------------------------------------------------------------------
    # Win condition
    # ------------------------------------------------------------------
    def check_winner(self) -> Optional[str]:
        alive = self.alive_players()
        mafia_alive = sum(1 for p in alive if p.role == MAFIA)
        town_alive = sum(1 for p in alive if p.role != MAFIA)

        if mafia_alive == 0:
            self.state = "ended"
            return "citizens"
        if mafia_alive >= town_alive:
            self.state = "ended"
            return "mafia"
        return None

    def summary(self) -> str:
        lines = []
        for p in self.players.values():
            status = "✅" if p.alive else "💀"
            lines.append(f"{status} {p.name} — {p.role.emoji} {p.role.name}")
        return "\n".join(lines)
