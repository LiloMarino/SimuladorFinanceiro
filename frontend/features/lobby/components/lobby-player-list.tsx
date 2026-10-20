import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";
import { TriangleAlert } from "lucide-react";
import { GroupingBadge } from "@/shared/components/grouping-badge";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Status } from "@/shared/components/ui/status";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { MAX_PLAYERS } from "@/shared/lib/player-colors";
import { teamColor } from "@/shared/lib/teams";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { cn } from "@/shared/lib/utils";
import type { PlayerGrouping, RoomPlayer, TeamNaming } from "@/types";
import { useApplyColorPreference } from "../hooks/useApplyColorPreference";
import { checkTeams } from "../lib/teams-check";
import { joinNames } from "../lib/join-names";
import { LobbyColorPicker } from "./lobby-color-picker";
import { LobbyTeamPicker } from "./lobby-team-picker";

type LobbyPlayersListProps = {
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
  hostNickname,
  savedPlayers,
  selectedSimulationId,
  grouping,
  naming,
}: LobbyPlayersListProps) {
  const { user } = useAuth();
  const { data: players } = useRoomPlayers();
  const { data: savedSimulations } = useQuery(simulationListOptions());
  const simulationName = savedSimulations?.find((s) => s.id === selectedSimulationId)?.name;

  // Em equipes, quem vê vem primeiro e ocupa a linha toda (cabem a cor e a equipe); depois o host e quem joga, em ordem alfabética
  const inTeams = grouping === "TEAMS";
  const rank = (nickname: string) =>
    Number(inTeams && nickname === user?.nickname) * 2 + Number(nickname === hostNickname);
  const sorted = [...(players ?? [])].sort((a, b) => rank(b.nickname) - rank(a.nickname) || a.nickname.localeCompare(b.nickname));

  // Quem jogou a partida selecionada e não está na sala segue dono da vaga e da cor
  const absent = savedPlayers.filter((saved) => !sorted.some((p) => p.nickname === saved.nickname));
  const occupied = sorted.length + absent.length;
  const alone = sorted.length <= 1 && absent.length === 0;
  // O convite de "sozinho" ocupa uma vaga livre, para a grade fechar em MAX_PLAYERS células
  const freeSlots = Math.max(MAX_PLAYERS - occupied - Number(alone), 0);
  const full = occupied >= MAX_PLAYERS;
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
          {absent.length > 0 && (
            <span className="text-xs text-muted-foreground">
              {sorted.length} na sala · {absent.length} offline da partida selecionada
            </span>
          )}
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
            const isHost = player.nickname === hostNickname;
            const isNew = savedPlayers.length > 0 && !savedPlayers.some((p) => p.nickname === player.nickname);
            return (
              <div
                key={player.nickname}
                style={inTeams && player.team ? ({ "--team": teamColor(player.team) } as CSSProperties) : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-[10px] border p-3",
                  isYou ? "border-info-border bg-info-soft" : "border-border bg-card",
                  inTeams && player.team && "border-l-[3px] border-l-(--team)",
                  inTeams && isYou && "col-span-2",
                )}
              >
                <PlayerAvatar nickname={player.nickname} color={player.color} size="lg" />
                <div className="grid min-w-0 flex-1">
                  <span className="truncate font-semibold">
                    {player.nickname}
                    {isYou && <span className="font-normal text-secondary-foreground"> (você)</span>}
                    {isNew && (
                      <Badge variant="info" size="sm" className="ml-1.5 align-[1px]">
                        Novo
                      </Badge>
                    )}
                  </span>
                  {isHost ? (
                    <span className="text-xs font-medium text-info">Host</span>
                  ) : (
                    <Status status="online">Online</Status>
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
                  inTeams && <TeamBadge team={player.team} naming={naming} />
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
                <span className="truncate font-semibold text-muted-foreground">{player.nickname}</span>
                <Status status="offline">Offline</Status>
              </div>
              {inTeams && <TeamBadge team={player.team} naming={naming} />}
            </div>
          ))}

          {/* Convite de quem está sozinho na sala: conta como uma vaga */}
          {alone && (
            <div
              className={cn(
                "grid content-center gap-1 rounded-[10px] border border-dashed border-info-border bg-info-soft/40 p-3",
                inTeams && "col-span-2",
              )}
            >
              <span className="font-semibold">Só você por aqui</span>
              <span className="text-[13px] text-muted-foreground">
                Mande o link acima pra quem vai jogar. Também dá pra jogar sozinho.
              </span>
            </div>
          )}

          {Array.from({ length: freeSlots }, (_, i) => (
            <div
              key={i}
              className="flex h-14.5 items-center justify-center rounded-[10px] border border-dashed border-input text-[13px] text-faint-foreground"
            >
              Vaga livre
            </div>
          ))}
        </div>

        {/* Avisos das equipes: quem falta, equipe única e equipes desiguais */}
        {inTeams && teams.missing.length > 0 && (
          <Alert variant="warning" className="mt-4">
            <TriangleAlert />
            <AlertTitle>
              {teams.missing.length} sem equipe:{" "}
              {joinNames(teams.missing.map((p) => (p.nickname === user?.nickname ? "você" : p.nickname)))}
            </AlertTitle>
            <AlertDescription>
              Cada um escolhe a sua no próprio card. Para não esperar, “Distribuir quem falta” põe cada um na equipe
              com menos gente.
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
              Equipes desiguais: {teams.sizes.length === 2 ? teams.sizes.join(" contra ") : joinNames(teams.sizes.map(String))}
            </AlertTitle>
            <AlertDescription>
              Dá pra jogar assim. A nota da equipe é a <strong>média</strong> dos membros, então a equipe maior não
              ganha por somar mais; na menor, cada um pesa mais na média.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
