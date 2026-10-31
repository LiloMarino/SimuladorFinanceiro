import { useState, type CSSProperties } from "react";
import { Info, Plus, TriangleAlert } from "lucide-react";
import { GroupingBadge } from "@/shared/components/grouping-badge";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Status } from "@/shared/components/ui/status";
import { PlayerActivityStatus } from "@/shared/components/player-activity-status";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { MAX_PLAYERS } from "@/shared/lib/player-colors";
import { plural } from "@/shared/lib/strategy-orders";
import { teamColor } from "@/shared/lib/teams";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import { cn } from "@/shared/lib/utils";
import type { PlayerGrouping, RoomPlayer, TeamNaming } from "@/types";
import { useApplyColorPreference } from "../hooks/useApplyColorPreference";
import { checkTeams } from "../lib/teams-check";
import { joinNames } from "../lib/join-names";
import { LobbyBotDialog } from "./lobby-bot-dialog";
import { LobbyBotMenu } from "./lobby-bot-menu";
import { LobbyColorPicker } from "./lobby-color-picker";
import { LobbyPlayerMenu } from "./lobby-player-menu";
import { LobbyTeamPicker } from "./lobby-team-picker";

type LobbyPlayersListProps = {
  isHost: boolean;
  hostNickname: string;
  /** Quem jogou a partida salva selecionada, com a cor guardada */
  savedPlayers: RoomPlayer[];
  /** Partida salva selecionada; nula quando a partida é nova */
  selectedSimulationId: number | null;
  /** Como a sala joga e como as equipes se chamam */
  grouping: PlayerGrouping;
  naming: TeamNaming;
};

/** Jogadores da sala em cartões, com as vagas livres à vista. */
export function LobbyPlayersList({
  isHost,
  hostNickname,
  savedPlayers,
  selectedSimulationId,
  grouping,
  naming,
}: LobbyPlayersListProps) {
  const { user } = useAuth();
  const { data: players } = useRoomPlayers();
  const { data: savedSimulations } = useSimulationList();
  const simulationName = savedSimulations?.find((s) => s.id === selectedSimulationId)?.name;

  // Em equipes, quem vê vem primeiro e ocupa a linha toda (cabem a cor e a equipe); depois o host e quem joga, em ordem alfabética
  const inTeams = grouping === "TEAMS";
  const rank = (nickname: string) =>
    Number(inTeams && nickname === user?.nickname) * 2 + Number(nickname === hostNickname);
  // Pessoas primeiro; os bots vêm depois, na ordem em que entraram
  const humans = [...(players ?? [])]
    .filter((p) => !p.bot)
    .sort((a, b) => rank(b.nickname) - rank(a.nickname) || a.nickname.localeCompare(b.nickname));
  const bots = (players ?? []).filter((p) => p.bot);
  const sorted = [...humans, ...bots];
  const [botDialog, setBotDialog] = useState<{ bot?: RoomPlayer } | null>(null);

  // Quem jogou a partida selecionada e não está na sala segue dono da vaga e da cor
  const absent = savedPlayers.filter((saved) => !sorted.some((p) => p.nickname === saved.nickname));
  const occupied = sorted.length + absent.length;
  const alone = sorted.length <= 1 && absent.length === 0;
  const freeSlots = Math.max(MAX_PLAYERS - occupied, 0);
  const full = occupied >= MAX_PLAYERS;
  // A partida salva traz os bots dela; a sala só ganha bots novos numa partida nova
  const canAddBot = isHost && selectedSimulationId === null && !full;
  const teams = checkTeams(sorted, savedPlayers, naming);

  const me = sorted.find((p) => p.nickname === user?.nickname);
  useApplyColorPreference(
    me,
    savedPlayers.some((p) => p.nickname === me?.nickname),
  );

  return (
    <Card>
      <CardHeader>
        <div className="grid gap-1">
          <CardTitle>Jogadores</CardTitle>
          <CardDescription>
            {plural(humans.length, "pessoa", "pessoas")}
            {bots.length > 0 && ` e ${plural(bots.length, "bot", "bots")}`}
            {absent.length > 0 && ` · ${absent.length} offline da partida selecionada`}
          </CardDescription>
        </div>
        <CardAction>
          <span className="flex items-center gap-2">
            <GroupingBadge grouping={grouping} />
            {full && <Badge variant="warning">Sala cheia</Badge>}
            <span className="font-mono text-muted-foreground">
              {occupied} / {MAX_PLAYERS}
            </span>
          </span>
        </CardAction>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 gap-2.5">
          {sorted.map((player) => {
            const isYou = player.nickname === user?.nickname;
            const isRoomHost = player.nickname === hostNickname;
            const isNew = savedPlayers.length > 0 && !savedPlayers.some((p) => p.nickname === player.nickname);
            const bot = player.bot;
            return (
              <div
                key={player.nickname}
                style={inTeams && player.team ? ({ "--team": teamColor(player.team) } as CSSProperties) : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-[10px] border p-3",
                  isYou ? "border-info-border bg-info-soft" : bot ? "border-border bg-subtle" : "border-border bg-card",
                  inTeams && player.team && "border-l-[3px] border-l-(--team)",
                  isYou && "col-span-2",
                )}
              >
                <PlayerAvatar nickname={player.nickname} color={player.color} bot={!!bot} size="lg" />
                <div className="grid min-w-0 flex-1 gap-0.5">
                  <span className="flex min-w-0 items-center gap-1.5">
                    <span className="min-w-0 truncate font-semibold" title={player.nickname}>
                      {player.nickname}
                      {isYou && <span className="font-normal text-secondary-foreground"> (você)</span>}
                    </span>
                    {bot && (
                      <Badge variant="secondary" size="tag" className="shrink-0">
                        Bot
                      </Badge>
                    )}
                    {isRoomHost && (
                      <Badge variant="info" size="sm" className="shrink-0">
                        Host
                      </Badge>
                    )}
                    {isNew && (
                      <Badge variant="info" size="sm" className="shrink-0">
                        Novo
                      </Badge>
                    )}
                  </span>
                  {bot ? (
                    <span className="truncate text-xs text-muted-foreground" title={bot.strategy_name}>
                      {bot.strategy_name}
                    </span>
                  ) : (
                    <PlayerActivityStatus activity={player.activity} />
                  )}
                </div>
                {isYou ? (
                  <div className="flex items-center gap-1.5">
                    <LobbyColorPicker
                      nickname={player.nickname}
                      players={sorted}
                      savedPlayers={savedPlayers}
                      simulationName={simulationName}
                    />
                    {inTeams && (
                      <LobbyTeamPicker
                        nickname={player.nickname}
                        players={sorted}
                        savedPlayers={savedPlayers}
                        naming={naming}
                        simulationName={simulationName}
                      />
                    )}
                  </div>
                ) : (
                  <div className="flex items-center gap-1.5">
                    {inTeams && <TeamBadge team={player.team} naming={naming} />}
                    {bot && isHost && !bot.locked && (
                      <LobbyBotMenu player={player} onConfigure={() => setBotDialog({ bot: player })} />
                    )}
                    {!bot && isHost && !isRoomHost && <LobbyPlayerMenu player={player} />}
                  </div>
                )}
              </div>
            );
          })}

          {/* Ausentes da partida selecionada: a cor e a vaga ficam reservadas */}
          {absent.map((player) => (
            <div
              key={player.nickname}
              style={inTeams && player.team ? ({ "--team": teamColor(player.team) } as CSSProperties) : undefined}
              className={cn(
                "flex items-center gap-3 rounded-[10px] border border-dashed border-input p-3",
                inTeams && player.team && "border-l-[3px] border-l-(--team)",
              )}
            >
              <span className="opacity-45">
                <PlayerAvatar nickname={player.nickname} color={player.color} size="lg" />
              </span>
              <div className="grid min-w-0 flex-1">
                <span className="truncate font-semibold text-muted-foreground" title={player.nickname}>
                  {player.nickname}
                </span>
                <Status status="offline">Offline</Status>
              </div>
              {inTeams && <TeamBadge team={player.team} naming={naming} />}
            </div>
          ))}

          {Array.from({ length: freeSlots }, (_, i) =>
            i === 0 && canAddBot ? (
              <button
                key={i}
                type="button"
                onClick={() => setBotDialog({})}
                className="flex h-16.5 cursor-pointer items-center justify-center gap-2 rounded-[10px] border border-dashed border-info-border bg-info-soft/50 text-[13px] font-semibold text-primary outline-none hover:border-solid hover:border-primary hover:bg-info-soft focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                <Plus className="size-4" />
                Adicionar bot
              </button>
            ) : (
              <div
                key={i}
                className="flex h-16.5 items-center justify-center rounded-[10px] border border-dashed border-input text-[13px] text-faint-foreground"
              >
                Vaga livre
              </div>
            ),
          )}
        </div>

        {/* Convite de quem está sozinho na sala */}
        {alone && (
          <Alert variant="muted" className="mt-3.5">
            <Info />
            <AlertTitle>Só você por aqui</AlertTitle>
            <AlertDescription>
              {isHost
                ? "Convide pelo link ou jogue contra bots: cada bot é uma estratégia do app."
                : "Mande o link acima pra quem vai jogar. Também dá pra jogar sozinho."}
            </AlertDescription>
          </Alert>
        )}

        {/* Sala cheia: o host só põe outro bot se abrir uma vaga */}
        {full && isHost && selectedSimulationId === null && (
          <p className="mt-3.5 flex items-center gap-2 rounded-lg bg-subtle px-2.5 py-2 text-xs text-muted-foreground">
            <Info className="size-3.5 shrink-0" />
            Sala cheia: para pôr outro bot, remova um jogador ou um bot (⋯ no cartão).
          </p>
        )}

        {/* Avisos das equipes: quem falta, equipe única e equipes desiguais */}
        {inTeams && teams.missing.length > 0 && (
          <Alert variant="warning" className="mt-4">
            <TriangleAlert />
            <AlertTitle>
              {teams.missing.length} sem equipe:{" "}
              {joinNames(teams.missing.map((p) => (p.nickname === user?.nickname ? "você" : p.nickname)))}
            </AlertTitle>
            <AlertDescription>
              Cada um escolhe a sua no próprio card. Para não esperar, “Distribuir quem falta” põe cada um na equipe com
              menos gente.
            </AlertDescription>
          </Alert>
        )}
        {inTeams && teams.single && (
          <Alert variant="destructive" className="mt-4">
            <TriangleAlert />
            <AlertTitle>Todos estão na {teams.singleName}</AlertTitle>
            <AlertDescription>
              Em equipes, a partida precisa de pelo menos duas. Alguém troca de equipe, ou o host volta para “Todos
              contra todos” nas regras.
            </AlertDescription>
          </Alert>
        )}
        {inTeams && teams.uneven && (
          <Alert variant="warning" className="mt-4">
            <TriangleAlert />
            <AlertTitle>
              Equipes desiguais:{" "}
              {teams.sizes.length === 2 ? teams.sizes.join(" contra ") : joinNames(teams.sizes.map(String))}
            </AlertTitle>
            <AlertDescription>
              Dá pra jogar assim. A nota da equipe é a <strong>média</strong> dos membros, então a equipe maior não
              ganha por somar mais; na menor, cada um pesa mais na média.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>

      <LobbyBotDialog
        open={botDialog !== null}
        onOpenChange={(open) => !open && setBotDialog(null)}
        bot={botDialog?.bot}
        grouping={grouping}
        naming={naming}
      />
    </Card>
  );
}
