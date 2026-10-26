import logging
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date
from itertools import count
from threading import Lock
from typing import ClassVar
from uuid import UUID, uuid4

from backend.config import toml as app_toml
from backend.core import repository
from backend.core.dto.bot import RoomBotDTO
from backend.core.dto.strategy import StrategyParamValue
from backend.core.dto.user import UserDTO
from backend.core.enum import PlayerActivity, PlayerGrouping
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    LockedError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.player_colors import MAX_PLAYERS, PLAYER_COLORS, first_free_color
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.teams import MIN_TEAMS, TEAM_COUNT, is_valid_team
from backend.core.utils.lazy_dict import LazyDict
from backend.features.strategy import catalog
from backend.features.strategy.registry import get_strategy

logger = logging.getLogger(__name__)

ROOM_FULL = (
    f"A sala está cheia: {MAX_PLAYERS} de {MAX_PLAYERS} jogadores. "
    "Peça pro host liberar uma vaga ou crie sua própria sala."
)
ROOM_RESERVED = (
    "As {n} vagas que restam são de quem jogou a partida selecionada e está offline. "
    "Peça pro host escolher outra partida ou espere essas pessoas voltarem."
)
BOT_NAME_TAKEN = "Já tem um jogador com esse nome na sala. Sorteie outro ou mude."
BOT_NAME_MAX = 30


@dataclass(frozen=True)
class BotConfig:
    """A estratégia do bot, com os parâmetros já completos pelo catálogo."""

    strategy_key: str
    params: dict[str, StrategyParamValue]
    # Bot da partida salva selecionada
    locked: bool = False


@dataclass(frozen=True)
class ParkedBot:
    """Bot de partida nova guardado enquanto uma partida salva está selecionada."""

    user: UserDTO
    config: BotConfig
    color: str
    team: int | None


class UserManager:
    """
    Gerenciador singleton de usuários e presença de players.

    Responsável por:
    - Controlar players ativos (autenticados e conectados) na simulação
    - Manter cache lazy de usuários por client_id para acesso rápido
    - Gerenciar lifecycle de conexão (register, unregister, auth, logout)
    - Emitir eventos de entrada/saída de players
    - Sincronizar estado com a simulação ativa
    - Dar a cada player da sala uma cor exclusiva da paleta
    - Guardar a equipe de cada player quando a sala joga em equipes
    - Guardar o que cada player está fazendo, aba por aba, e avisar a sala quando muda
    - Manter os bots da sala: jogadores sem pessoa por trás, que moram em `_active_players`
      como os demais e saem dela na largada
    """

    # 🔹 Apenas players autenticados (presença)
    _active_players: ClassVar[dict[UUID, UserDTO]] = {}

    # 🔹 Cor de cada player da sala (user_id -> chave da paleta); a sala não repete cor
    _colors: ClassVar[dict[int, str]] = {}

    # 🔹 Cores guardadas da partida salva selecionada, inclusive de quem está ausente:
    # quem participou fica travado nelas e ninguém mais toma essas cores
    _saved_colors: ClassVar[dict[int, str]] = {}

    # 🔹 Equipe de cada player da sala (user_id -> 1..10); só existe no modo em equipes e
    # sobrevive à desconexão, para quem recarrega a página voltar para a mesma equipe
    _teams: ClassVar[dict[int, int]] = {}

    # 🔹 Equipes guardadas da partida salva selecionada: quem já jogou fica travado nelas
    _saved_teams: ClassVar[dict[int, int]] = {}

    # 🔹 O que cada aba aberta do player está fazendo (client_id -> sid -> (ordem do aviso, atividade));
    # só memória. O selo da sala é o da aba mais relevante: aba à vista ganha de ausente, e entre
    # as à vista vale o aviso mais recente
    _activities: ClassVar[dict[UUID, dict[str, tuple[int, PlayerActivity | None]]]] = {}
    _activity_order = count()

    # 🔹 Os bots da sala (client_id -> estratégia); o usuário do bot está em `_active_players`
    _bots: ClassVar[dict[UUID, BotConfig]] = {}

    # 🔹 Bots de partida nova guardados enquanto há partida salva selecionada; voltam
    # à sala quando a seleção sai
    _parked_bots: ClassVar[dict[UUID, ParkedBot]] = {}

    # 🔹 Cache lazy client_id -> UserDTO (independente de presença)
    _client_user_cache: LazyDict[UUID, UserDTO | None] = LazyDict(
        loader=repository.user.get_by_client_id
    )

    _lock = Lock()

    # =========================
    # Conexão
    # =========================

    @classmethod
    def unregister(cls, client_id: UUID):
        with cls._lock:
            player = cls._active_players.pop(client_id, None)
            color = cls._colors.pop(player.id, None) if player else None
            cls._activities.pop(client_id, None)

        if player and color:
            cls._emit_player_exit(player, color)

    # =========================
    # Autenticação
    # =========================

    @classmethod
    def player_auth(cls, client_id: UUID) -> UserDTO | None:
        user = cls.get_user(client_id)
        if user is None:
            return None

        with cls._lock:
            if client_id in cls._active_players:
                return user

        # Com partida em andamento a cor é a da partida
        match_colors = cls._match_colors()

        # Quem não joga a partida entra autenticado, sem vaga na sala: a cor ele escolhe em join_match
        if match_colors is not None and user.id not in match_colors:
            if len(match_colors) >= MAX_PLAYERS:
                raise LockedError(cls._match_full())
            return user

        with cls._lock:
            if client_id in cls._active_players:
                return user

            if (
                len(cls._active_players) >= MAX_PLAYERS
                or cls._people_count() + len(cls._parked_bots) >= MAX_PLAYERS
            ):
                raise LockedError(ROOM_FULL)

            if match_colors is not None:
                color = match_colors[user.id]
            elif user.id in cls._saved_colors:
                color = cls._saved_colors[user.id]
            else:
                color = cls._free_color()

            cls._active_players[client_id] = user
            cls._colors[user.id] = color

        cls._emit_player_join(user, color)
        return user

    @classmethod
    def player_logout(cls, client_id: UUID):
        with cls._lock:
            # Remove presença ativa (se existir)
            user = cls._active_players.pop(client_id, None)
            color = cls._colors.pop(user.id, None) if user else None
            cls._activities.pop(client_id, None)

        # Limpa caches da simulação (se houver simulação ativa)
        try:
            sim = SimulationManager.get_active_simulation()
            sim.clear_user_cache(client_id)
        except NoActiveSimulationError:
            pass

        # Emite evento de saída se o usuário estava ativo
        if user and color:
            cls._emit_player_exit(user, color)

        # Limpa cache lazy (força sessão a virar "guest")
        cls._client_user_cache.pop(client_id, None)

        logger.info("Usuário saiu (logout): client_id=%s", client_id)

    @classmethod
    def remove_player(cls, nickname: str) -> None:
        """
        O host tira uma pessoa da sala, no lobby. Sai pelo caminho do logout (a vaga e a
        cor ficam livres na hora) e o próprio jogador é avisado para encerrar a sessão.
        O usuário e o histórico dele ficam: só a presença na sala acaba.
        """
        if SimulationManager.has_active_simulation():
            raise ConflictError(
                "A partida já começou: só dá para remover alguém no lobby."
            )
        if nickname == app_toml.host.nickname:
            raise ConflictError("O host não se remove da sala.")

        with cls._lock:
            client_id = next(
                (
                    cid
                    for cid, p in cls._active_players.items()
                    if cid not in cls._bots and p.nickname == nickname
                ),
                None,
            )
        if client_id is None:
            raise NotFoundError("Esse jogador não está na sala.")

        cls.player_logout(client_id)
        cls._emit_player_removed(nickname, client_id)

    @classmethod
    def is_pending_join(cls, user: UserDTO) -> bool:
        """Há partida em andamento e `user` não joga nela: precisa escolher uma cor em join_match."""
        match_colors = cls._match_colors()
        return match_colors is not None and user.id not in match_colors

    @classmethod
    def join_match(cls, client_id: UUID, color: str, team: int | None = None) -> None:
        """
        Entra na partida em andamento com `color` (e `team`, em partida em equipes).
        A cor vale para quem pediu primeiro: o teto da partida e a cor livre são
        conferidos e gravados sob o mesmo lock, então dois chegando juntos não passam
        da última vaga nem repetem cor.
        """
        if color not in PLAYER_COLORS:
            raise UnprocessableEntityError("Essa cor não existe na paleta.")

        user = cls.get_user(client_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado.")
        if not SimulationManager.has_active_simulation():
            raise ConflictError("Não há partida em andamento.")

        sim = SimulationManager.get_active_simulation()
        simulation_id = SimulationManager.get_active_simulation_id()

        in_teams = sim.settings.player_grouping is PlayerGrouping.TEAMS
        if in_teams and (team is None or not is_valid_team(team)):
            raise UnprocessableEntityError("Escolha uma equipe para entrar.")

        with cls._lock:
            colors = repository.simulation_player.colors(simulation_id)
            if user.id in colors:
                raise ConflictError("Você já faz parte da partida.")
            if len(colors) >= MAX_PLAYERS:
                raise LockedError(cls._match_full())

            owner_id = next((uid for uid, c in colors.items() if c == color), None)
            if owner_id is not None:
                owner = next(
                    p.nickname
                    for p in repository.simulation_player.participants(simulation_id)
                    if p.id == owner_id
                )
                raise ConflictError(f"{owner} pegou essa cor antes.")

            repository.simulation_player.save(
                simulation_id,
                {user.id: color},
                {user.id: team} if in_teams and team is not None else None,
            )
            cls._active_players[client_id] = user
            cls._colors[user.id] = color

        # Depósito e snapshot do dia: o motor tem o próprio lock, fora do nosso
        sim.add_player(user)
        cls._emit_player_join(user, color)

    # =========================
    # Queries
    # =========================

    @classmethod
    def get_user(cls, client_id: UUID) -> UserDTO | None:
        user = cls._client_user_cache[client_id]
        if user is None:
            cls._client_user_cache.pop(client_id, None)
            return None
        return user

    @classmethod
    def get_user_id(cls, client_id: UUID) -> int:
        user = cls.get_user(client_id)
        if user is None:
            raise NotFoundError(f"Usuário não encontrado para client_id={client_id}")
        return user.id

    @classmethod
    def list_active_players(cls) -> list[UserDTO]:
        with cls._lock:
            return list(cls._active_players.values())

    # =========================
    # Atividade
    # =========================

    @classmethod
    def set_activity(
        cls, client_id: UUID, sid: str, activity: PlayerActivity | None
    ) -> None:
        """A aba `sid` avisa o que está fazendo; a sala só ouve quando o selo do player muda."""
        with cls._lock:
            tabs = cls._activities.setdefault(client_id, {})
            before = cls._resolve_activity(tabs)
            tabs[sid] = (next(cls._activity_order), activity)
            after = cls._resolve_activity(tabs)
            player = cls._active_players.get(client_id)

        if player and before != after:
            cls._emit_player_activity(player, after)

    @classmethod
    def drop_activity(cls, client_id: UUID, sid: str) -> None:
        """A aba `sid` fechou e o player segue em outra: o selo passa a ser o das que restam."""
        with cls._lock:
            tabs = cls._activities.get(client_id)
            if tabs is None or sid not in tabs:
                return
            before = cls._resolve_activity(tabs)
            del tabs[sid]
            after = cls._resolve_activity(tabs)
            if not tabs:
                del cls._activities[client_id]
            player = cls._active_players.get(client_id)

        if player and before != after:
            cls._emit_player_activity(player, after)

    @classmethod
    def room_activities(cls) -> dict[int, PlayerActivity | None]:
        """Atividade de cada player da sala, por user_id; nulo é "Online"."""
        with cls._lock:
            return {
                player.id: cls._resolve_activity(cls._activities.get(client_id))
                for client_id, player in cls._active_players.items()
            }

    @staticmethod
    def _resolve_activity(
        tabs: dict[str, tuple[int, PlayerActivity | None]] | None,
    ) -> PlayerActivity | None:
        if not tabs:
            return None
        in_view = [t for t in tabs.values() if t[1] is not PlayerActivity.AWAY]
        return max(in_view or tabs.values(), key=lambda tab: tab[0])[1]

    # =========================
    # Cores
    # =========================

    @classmethod
    def get_color(cls, user_id: int) -> str | None:
        """Cor na sala; quem saiu no meio da partida mantém a da partida."""
        with cls._lock:
            color = cls._colors.get(user_id)
        if color is None:
            color = (cls._match_colors() or {}).get(user_id)
        return color

    @classmethod
    def room_colors(cls) -> dict[int, str]:
        """Cor de cada player da sala, por user_id."""
        with cls._lock:
            return dict(cls._colors)

    @classmethod
    def set_color(cls, client_id: UUID, color: str) -> None:
        """A cor é de quem pediu primeiro: se já tem dono, quem pediu fica com a que tinha."""
        if color not in PLAYER_COLORS:
            raise UnprocessableEntityError("Essa cor não existe na paleta.")

        if SimulationManager.has_active_simulation():
            raise ConflictError("A partida já começou: as cores ficam travadas.")

        with cls._lock:
            player = cls._active_players.get(client_id)
            if player is None:
                raise NotFoundError("Você não está na sala.")

            if player.id in cls._saved_colors:
                raise ConflictError("Sua cor é a da partida selecionada.")

            if cls._colors.get(player.id) == color:
                return

            owner = next(
                (
                    p.nickname
                    for p in cls._active_players.values()
                    if cls._colors.get(p.id) == color
                ),
                None,
            )
            if owner is not None:
                raise ConflictError(f"{owner} pegou essa cor antes.")

            if color in cls._saved_colors.values():
                raise ConflictError("Essa cor é de um jogador da partida selecionada.")

            cls._colors[player.id] = color

        cls._emit_player_color(player, color, cls.get_team(player.id))

    @classmethod
    def apply_saved_colors(
        cls,
        colors: dict[int, str],
        teams: dict[int, int] | None = None,
        bots: list[tuple[UserDTO, BotConfig]] | None = None,
    ) -> None:
        """
        Ao selecionar uma partida salva: quem já jogou volta com a cor (e a equipe)
        guardada e fica travado; quem nunca jogou mantém a sua, se sobrou, ou ganha
        uma livre. Os bots da partida salva (`bots`) entram na sala travados; os de
        partida nova ficam guardados até a seleção sair.
        """
        saved_bots = bots or []
        with cls._lock:
            overflow = cls._overflow(colors)
            if overflow:
                free = MAX_PLAYERS - len(colors)
                raise ConflictError(
                    f"A partida tem {len(colors)} jogadores e só cabem mais {free}. "
                    f"Quem nunca jogou nela e está na sala: {', '.join(overflow)}."
                )
            clash = [
                bot.nickname
                for bot, _ in saved_bots
                if any(
                    p.nickname.casefold() == bot.nickname.casefold()
                    for p in cls._active_players.values()
                    if p.client_id not in cls._bots
                )
            ]
            if clash:
                raise ConflictError(
                    f"Já tem um jogador na sala com o nome de um bot da partida: {', '.join(clash)}."
                )

            left = cls._take_out_bots(park=True)
            newcomers = [p for p in cls._active_players.values() if p.id not in colors]

            before = dict(cls._colors)
            cls._saved_colors = dict(colors)
            cls._saved_teams = dict(teams or {})
            for player in cls._active_players.values():
                if player.id in colors:
                    cls._colors[player.id] = colors[player.id]
                if player.id in cls._saved_teams:
                    cls._teams[player.id] = cls._saved_teams[player.id]

            # Cores guardadas valem para quem jogou; as dos ausentes ficam reservadas
            taken = set(colors.values())
            for player in newcomers:
                mine = cls._colors[player.id]
                if mine in taken:
                    mine = first_free_color(taken | set(cls._colors.values()))
                    cls._colors[player.id] = mine
                taken.add(mine)

            changed = [
                (p, cls._colors[p.id])
                for p in cls._active_players.values()
                if before.get(p.id) != cls._colors[p.id]
            ]
            # A partida salva em equipes manda: fora dela ninguém tem equipe
            in_teams = bool(teams)
            effective = {
                p.id: cls._teams.get(p.id) if in_teams else None
                for p in cls._active_players.values()
            }
            players = list(cls._active_players.values())

            for bot, config in saved_bots:
                cls._active_players[bot.client_id] = bot
                cls._colors[bot.id] = colors[bot.id]
                cls._bots[bot.client_id] = replace(config, locked=True)
                if bot.id in cls._saved_teams:
                    cls._teams[bot.id] = cls._saved_teams[bot.id]

        for user, color, info in left:
            cls._emit_player_exit(user, color, info)
        for player, color in changed:
            cls._emit_player_color(player, color, effective[player.id])
        for player in players:
            cls._emit_player_team(player, effective[player.id])
        for bot, _ in saved_bots:
            cls._emit_player_join(bot, colors[bot.id])

    @classmethod
    def room_overflow(cls, colors: dict[int, str]) -> list[str]:
        """Apelidos de quem está na sala e nunca jogou a partida `colors`, quando ela não os comporta."""
        with cls._lock:
            return cls._overflow(colors)

    @classmethod
    def release_saved_colors(cls) -> None:
        """
        Sem partida selecionada as cores e as equipes da sala voltam a ser livres para
        trocar: os bots da partida salva saem e os de partida nova guardados voltam.
        """
        with cls._lock:
            cls._saved_colors = {}
            cls._saved_teams = {}
            left = cls._take_out_bots(park=False)
            restored, dropped = cls._restore_parked_bots()

        for user, color, info in left:
            cls._emit_player_exit(user, color, info)
        for user in restored:
            cls._emit_player_join(user, cls._colors[user.id])
        for user in dropped:
            repository.user.delete_user(user.id)

    # =========================
    # Equipes
    # =========================

    @classmethod
    def grouping(cls) -> PlayerGrouping:
        """Como a sala joga: a partida em andamento manda; sem ela vale a selecionada ou a nova."""
        if SimulationManager.has_active_simulation():
            return SimulationManager.get_active_simulation().settings.player_grouping
        return SettingsManager.effective_grouping()

    @classmethod
    def get_team(cls, user_id: int) -> int | None:
        """Equipe na sala; na partida em andamento vale a gravada nela. `None` fora do modo em equipes."""
        if cls.grouping() is not PlayerGrouping.TEAMS:
            return None
        match_teams = cls._match_teams()
        if match_teams is not None:
            return match_teams.get(user_id)
        with cls._lock:
            return cls._teams.get(user_id)

    @classmethod
    def room_teams(cls) -> dict[int, int]:
        """Equipe de cada player presente na sala, por user_id; vazio fora do modo em equipes."""
        if cls.grouping() is not PlayerGrouping.TEAMS:
            return {}
        return cls.chosen_teams()

    @classmethod
    def chosen_teams(cls) -> dict[int, int]:
        """Equipes que a sala escolheu, valham ou não para o agrupamento vigente (o host decide ao iniciar)."""
        with cls._lock:
            return {
                p.id: cls._teams[p.id]
                for p in cls._active_players.values()
                if p.id in cls._teams
            }

    @classmethod
    def set_team(cls, client_id: UUID, team: int) -> None:
        """Cada um escolhe a própria equipe; equipe não tem dono nem limite de membros."""
        if not is_valid_team(team):
            raise UnprocessableEntityError("Essa equipe não existe.")
        cls._ensure_teams_editable()

        with cls._lock:
            player = cls._active_players.get(client_id)
            if player is None:
                raise NotFoundError("Você não está na sala.")

            if player.id in cls._saved_teams:
                raise ConflictError("Sua equipe é a da partida selecionada.")

            if cls._teams.get(player.id) == team:
                return

            cls._teams[player.id] = team

        cls._emit_player_team(player, team)

    @classmethod
    def distribute_teams(cls) -> None:
        """
        Põe cada player sem equipe na equipe com menos gente. Sem equipes formadas, abre
        as duas primeiras; com uma só, abre mais uma para a partida poder começar.
        """
        cls._ensure_teams_editable()

        placed: list[tuple[UserDTO, int]] = []
        with cls._lock:
            missing = [
                p for p in cls._active_players.values() if p.id not in cls._teams
            ]
            counts = Counter(
                cls._teams[p.id]
                for p in cls._active_players.values()
                if p.id in cls._teams
            )
            pool = sorted(counts)
            for team in range(1, TEAM_COUNT + 1):
                if len(pool) >= MIN_TEAMS:
                    break
                if team not in counts:
                    pool.append(team)

            for player in missing:
                team = min(pool, key=lambda t: (counts[t], t))
                cls._teams[player.id] = team
                counts[team] += 1
                placed.append((player, team))

        for player, team in placed:
            cls._emit_player_team(player, team)

    @classmethod
    def reset_teams(cls) -> None:
        """Mudar o agrupamento da sala desfaz as equipes: nada foi jogado ainda."""
        with cls._lock:
            affected = [p for p in cls._active_players.values() if p.id in cls._teams]
            cls._teams.clear()

        for player in affected:
            cls._emit_player_team(player, None)

    @classmethod
    def release_room_teams(cls) -> None:
        """A partida começou: as equipes passam a morar nela e a próxima sala começa sem equipe."""
        with cls._lock:
            cls._teams.clear()

    @classmethod
    def ensure_teams_ready(cls, saved_teams: dict[int, int]) -> None:
        """
        Conferido ao iniciar em equipes: todo mundo na sala tem equipe (quem já jogou a
        partida salva traz a dela) e a partida tem pelo menos duas.
        """
        with cls._lock:
            teams = {
                p.nickname: saved_teams.get(p.id, cls._teams.get(p.id))
                for p in cls._active_players.values()
            }
        missing = [name for name, team in teams.items() if team is None]
        if missing:
            raise ConflictError(
                f"Para iniciar, todo mundo precisa estar numa equipe. Sem equipe: {', '.join(missing)}."
            )
        distinct = {team for team in teams.values() if team is not None}
        distinct |= set(saved_teams.values())
        if len(distinct) < MIN_TEAMS:
            raise ConflictError(
                "Em equipes, a partida precisa de pelo menos duas. "
                "Alguém troca de equipe, ou o host volta para todos contra todos."
            )

    @classmethod
    def _ensure_teams_editable(cls) -> None:
        if cls.grouping() is not PlayerGrouping.TEAMS:
            raise ConflictError("A sala joga todos contra todos: não há equipes.")
        if SimulationManager.has_active_simulation():
            raise ConflictError("A partida já começou: as equipes ficam travadas.")

    @classmethod
    def _match_teams(cls) -> dict[int, int] | None:
        """Equipes dos participantes da partida em andamento; `None` sem partida."""
        if not SimulationManager.has_active_simulation():
            return None
        return repository.simulation_player.teams(
            SimulationManager.get_active_simulation_id()
        )

    @classmethod
    def _match_colors(cls) -> dict[int, str] | None:
        """Cores dos participantes da partida em andamento; `None` sem partida."""
        if not SimulationManager.has_active_simulation():
            return None
        return repository.simulation_player.colors(
            SimulationManager.get_active_simulation_id()
        )

    @classmethod
    def _overflow(cls, colors: dict[int, str]) -> list[str]:
        """
        O chamador segura o `_lock`: ausentes da partida ocupam vaga, então novatos passam
        do teto. Bots não contam: os de partida nova ficam guardados na seleção.
        """
        newcomers = [
            p.nickname
            for p in cls._active_players.values()
            if p.id not in colors and p.client_id not in cls._bots
        ]
        return newcomers if len(colors) + len(newcomers) > MAX_PLAYERS else []

    @classmethod
    def _match_full(cls) -> str:
        """Partida sem vaga: participante offline também ocupa a sua."""
        return f"A partida já tem {MAX_PLAYERS} jogadores e está lotada."

    @classmethod
    def _free_color(cls) -> str:
        taken = set(cls._colors.values()) | set(cls._saved_colors.values())
        try:
            return first_free_color(taken)
        except ValueError:
            absent = sum(
                1 for user_id in cls._saved_colors if user_id not in cls._colors
            )
            if absent:
                raise LockedError(ROOM_RESERVED.format(n=absent)) from None
            raise LockedError(ROOM_FULL) from None

    # =========================
    # Bots
    # =========================

    @classmethod
    def add_bot(
        cls,
        nickname: str,
        strategy_key: str,
        params: dict[str, StrategyParamValue],
        color: str | None = None,
        team: int | None = None,
    ) -> UserDTO:
        """
        Põe na sala um bot novo: um usuário próprio, com a estratégia e a cor (a próxima
        livre, sem `color`). Nome, vaga e cor são conferidos e gravados sob o mesmo lock.
        """
        nickname = cls.bot_nickname(nickname)
        config = cls.bot_config(strategy_key, params)
        team = cls._bot_team(team)
        if cls._saved_colors:
            raise ConflictError(
                "Com uma partida salva selecionada os bots são os dela: não dá para adicionar outro."
            )
        cls._ensure_no_match()

        with cls._lock:
            if len(cls._active_players) >= MAX_PLAYERS:
                raise LockedError(ROOM_FULL)
            cls._ensure_name_free(nickname)
            chosen = cls._claim_color(color)
            bot = repository.user.create_user(uuid4(), nickname, is_bot=True)
            cls._active_players[bot.client_id] = bot
            cls._colors[bot.id] = chosen
            cls._bots[bot.client_id] = config
            if team is not None:
                cls._teams[bot.id] = team

        cls._client_user_cache[bot.client_id] = bot
        cls._emit_player_join(bot, chosen)
        return bot

    @classmethod
    def update_bot(
        cls,
        nickname: str,
        new_nickname: str,
        strategy_key: str,
        params: dict[str, StrategyParamValue],
        color: str | None = None,
        team: int | None = None,
    ) -> None:
        """Configura o bot da sala: estratégia, parâmetros, nome, cor e equipe. Sem `color`, fica a que tem."""
        new_nickname = cls.bot_nickname(new_nickname)
        config = cls.bot_config(strategy_key, params)
        team = cls._bot_team(team)

        with cls._lock:
            client_id, bot = cls._editable_bot(nickname)
            if new_nickname.casefold() != bot.nickname.casefold():
                cls._ensure_name_free(new_nickname)
            chosen = (
                cls._claim_color(color, owner_id=bot.id)
                if color
                else cls._colors[bot.id]
            )
            if new_nickname != bot.nickname:
                bot = repository.user.rename(bot.id, new_nickname)
            cls._active_players[client_id] = bot
            cls._colors[bot.id] = chosen
            cls._bots[client_id] = config
            if team is not None:
                cls._teams[bot.id] = team

        cls._client_user_cache[client_id] = bot
        cls._emit_player_bot(bot, chosen, previous_nickname=nickname)

    @classmethod
    def remove_bot(cls, nickname: str) -> None:
        """Tira o bot da sala e apaga o usuário dele: a vaga e a cor ficam livres."""
        with cls._lock:
            client_id, bot = cls._editable_bot(nickname)
            color = cls._colors.pop(bot.id)
            # O evento de saída leva a estratégia que o bot tinha
            info = cls.room_bot(bot)
            del cls._active_players[client_id]
            del cls._bots[client_id]
            cls._teams.pop(bot.id, None)
            cls._activities.pop(client_id, None)

        repository.user.delete_user(bot.id)
        cls._client_user_cache.pop(client_id, None)
        cls._emit_player_exit(bot, color, info)

    @classmethod
    def room_bots(cls) -> list[tuple[UserDTO, BotConfig]]:
        """Os bots da sala com a estratégia de cada um."""
        with cls._lock:
            return [
                (p, cls._bots[client_id])
                for client_id, p in cls._active_players.items()
                if client_id in cls._bots
            ]

    @classmethod
    def room_bot(cls, user: UserDTO) -> RoomBotDTO | None:
        """O bot como a lista da sala o mostra; nulo para quem é pessoa."""
        config = cls._bots.get(user.client_id)
        if config is None:
            return None
        return RoomBotDTO(
            strategy_key=config.strategy_key,
            strategy_name=get_strategy(config.strategy_key).name,
            params=config.params,
            locked=config.locked,
        )

    @classmethod
    def validate_bots(cls, start_date: date) -> None:
        """Conferido ao iniciar: as regras podem ter mudado desde que o bot entrou na sala."""
        for bot, config in cls.room_bots():
            try:
                cls.bot_config(config.strategy_key, config.params, start_date)
            except UnprocessableEntityError as error:
                raise UnprocessableEntityError(
                    f"{bot.nickname} não joga com as regras de agora: {error.detail}"
                ) from error

    @classmethod
    def release_bots(cls) -> None:
        """
        A partida começou: os bots passam a morar nela e a próxima sala começa só com
        as pessoas. Os guardados de partida nova nunca jogaram e somem. Os bots seguem
        jogando: a saída da sala não é um evento de jogador saindo, e os clientes
        refazem a lista de jogadores ao receber o início da partida.
        """
        with cls._lock:
            cls._take_out_bots(park=False)
            abandoned = list(cls._parked_bots.values())
            cls._parked_bots.clear()

        for parked in abandoned:
            repository.user.delete_user(parked.user.id)

    @classmethod
    def has_room_name(cls, nickname: str) -> bool:
        """Há alguém na sala com esse nome, bot ou pessoa."""
        with cls._lock:
            return cls._name_in_room(nickname)

    @classmethod
    def _take_out_bots(
        cls, *, park: bool
    ) -> list[tuple[UserDTO, str, RoomBotDTO | None]]:
        """
        O chamador segura o `_lock`: tira os bots da sala. Os de partida nova ficam
        guardados com `park`; os da partida salva nunca ficam.
        """
        left: list[tuple[UserDTO, str, RoomBotDTO | None]] = []
        for client_id in list(cls._bots):
            bot = cls._active_players[client_id]
            info = cls.room_bot(bot)
            config = cls._bots.pop(client_id)
            del cls._active_players[client_id]
            color = cls._colors.pop(bot.id)
            team = cls._teams.pop(bot.id, None)
            cls._activities.pop(client_id, None)
            left.append((bot, color, info))
            if park and not config.locked:
                cls._parked_bots[client_id] = ParkedBot(bot, config, color, team)
        return left

    @classmethod
    def _restore_parked_bots(cls) -> tuple[list[UserDTO], list[UserDTO]]:
        """
        O chamador segura o `_lock`: devolve à sala os bots guardados, na cor deles ou,
        se alguém a pegou, na primeira livre. O que não cabe mais sai (segundo valor).
        """
        restored: list[UserDTO] = []
        dropped: list[UserDTO] = []
        for client_id, parked in list(cls._parked_bots.items()):
            del cls._parked_bots[client_id]
            if len(cls._active_players) >= MAX_PLAYERS:
                dropped.append(parked.user)
                continue
            taken = set(cls._colors.values())
            color = (
                parked.color if parked.color not in taken else first_free_color(taken)
            )
            cls._active_players[client_id] = parked.user
            cls._colors[parked.user.id] = color
            cls._bots[client_id] = parked.config
            if parked.team is not None:
                cls._teams[parked.user.id] = parked.team
            restored.append(parked.user)
        return restored, dropped

    @classmethod
    def _editable_bot(cls, nickname: str) -> tuple[UUID, UserDTO]:
        """O chamador segura o `_lock`: o bot da sala com esse nome, se a sala ainda o deixa mexer."""
        found = next(
            (
                (client_id, p)
                for client_id, p in cls._active_players.items()
                if client_id in cls._bots and p.nickname == nickname
            ),
            None,
        )
        if found is None:
            raise NotFoundError("Esse bot não está na sala.")
        if cls._bots[found[0]].locked:
            raise ConflictError(
                "Esse bot é da partida selecionada: não dá para configurar nem remover."
            )
        cls._ensure_no_match()
        return found

    @classmethod
    def _ensure_no_match(cls) -> None:
        if SimulationManager.has_active_simulation():
            raise ConflictError("A partida já começou: os bots ficam travados.")

    @classmethod
    def bot_nickname(cls, nickname: str) -> str:
        nickname = nickname.strip()
        if not nickname or len(nickname) > BOT_NAME_MAX or {"#", "/"} & set(nickname):
            raise UnprocessableEntityError(
                f"O nome do bot precisa ter de 1 a {BOT_NAME_MAX} caracteres, sem # nem /."
            )
        return nickname

    @classmethod
    def bot_config(
        cls,
        strategy_key: str,
        params: dict[str, StrategyParamValue],
        today: date | None = None,
    ) -> BotConfig:
        """Os parâmetros completos pelo catálogo, na data das regras do lobby, e já validados."""
        strategy = get_strategy(strategy_key)
        known = catalog.known_tickers()
        resolved = catalog.with_defaults(
            strategy, params, today or SettingsManager.get().start_date, None, known
        )
        errors = strategy.validate(resolved, known)
        if errors:
            raise UnprocessableEntityError(" ".join(errors.values()))
        return BotConfig(strategy_key, resolved)

    @classmethod
    def _bot_team(cls, team: int | None) -> int | None:
        if cls.grouping() is not PlayerGrouping.TEAMS:
            return None
        if team is not None and not is_valid_team(team):
            raise UnprocessableEntityError("Essa equipe não existe.")
        return team

    @classmethod
    def _name_in_room(cls, nickname: str) -> bool:
        return any(
            p.nickname.casefold() == nickname.casefold()
            for p in cls._active_players.values()
        )

    @classmethod
    def _ensure_name_free(cls, nickname: str) -> None:
        if cls._name_in_room(nickname):
            raise ConflictError(BOT_NAME_TAKEN)

    @classmethod
    def _claim_color(cls, color: str | None, owner_id: int | None = None) -> str:
        """O chamador segura o `_lock`: a cor pedida se está livre (a do próprio dono vale), ou a próxima livre."""
        if color is None:
            return cls._free_color()
        if color not in PLAYER_COLORS:
            raise UnprocessableEntityError("Essa cor não existe na paleta.")
        owner = next(
            (
                p.nickname
                for p in cls._active_players.values()
                if p.id != owner_id and cls._colors.get(p.id) == color
            ),
            None,
        )
        if owner is not None:
            raise ConflictError(f"{owner} pegou essa cor antes.")
        return color

    @classmethod
    def _people_count(cls) -> int:
        """O chamador segura o `_lock`: quem está na sala sem ser bot."""
        return sum(1 for client_id in cls._active_players if client_id not in cls._bots)

    # =========================
    # Eventos
    # =========================

    @classmethod
    def _emit_player_join(cls, user: UserDTO, color: str):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info("Jogador entrou na partida: %s", user.nickname)
        notify(
            "player_join",
            PlayerPresenceEventDTO(
                nickname=user.nickname,
                color=color,
                team=cls.get_team(user.id),
                activity=cls.room_activities().get(user.id),
                bot=cls.room_bot(user),
            ).to_json(),
        )

    @classmethod
    def _emit_player_exit(
        cls, user: UserDTO, color: str, bot: RoomBotDTO | None = None
    ):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info("Jogador saiu da partida: %s", user.nickname)
        notify(
            "player_exit",
            PlayerPresenceEventDTO(
                nickname=user.nickname, color=color, bot=bot
            ).to_json(),
        )

    @classmethod
    def _emit_player_removed(cls, nickname: str, client_id: UUID):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerRemovedEventDTO,
        )

        logger.info("Jogador removido da sala pelo host: %s", nickname)
        notify(
            "player_removed",
            PlayerRemovedEventDTO(nickname=nickname).to_json(),
            to=client_id,
        )

    @classmethod
    def _emit_player_color(cls, user: UserDTO, color: str, team: int | None):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        notify(
            "player_color",
            PlayerPresenceEventDTO(
                nickname=user.nickname,
                color=color,
                team=team,
                activity=cls.room_activities().get(user.id),
                bot=cls.room_bot(user),
            ).to_json(),
        )

    @classmethod
    def _emit_player_team(cls, user: UserDTO, team: int | None):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        color = cls.get_color(user.id)
        if color is None:
            return
        notify(
            "player_team",
            PlayerPresenceEventDTO(
                nickname=user.nickname,
                color=color,
                team=team,
                activity=cls.room_activities().get(user.id),
                bot=cls.room_bot(user),
            ).to_json(),
        )

    @classmethod
    def _emit_player_activity(cls, user: UserDTO, activity: PlayerActivity | None):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        color = cls.get_color(user.id)
        if color is None:
            return
        notify(
            "player_activity",
            PlayerPresenceEventDTO(
                nickname=user.nickname,
                color=color,
                team=cls.get_team(user.id),
                activity=activity,
                bot=cls.room_bot(user),
            ).to_json(),
        )

    @classmethod
    def _emit_player_bot(cls, user: UserDTO, color: str, *, previous_nickname: str):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        notify(
            "player_bot",
            PlayerPresenceEventDTO(
                nickname=user.nickname,
                previous_nickname=previous_nickname,
                color=color,
                team=cls.get_team(user.id),
                activity=cls.room_activities().get(user.id),
                bot=cls.room_bot(user),
            ).to_json(),
        )
