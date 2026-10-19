import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { DoorOpen, TriangleAlert } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { PlayerColorGrid } from "@/shared/components/player-color-grid";
import { TeamBadge } from "@/shared/components/team-badge";
import { TeamGrid } from "@/shared/components/team-grid";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { Status } from "@/shared/components/ui/status";
import { ErrorState } from "@/shared/components/error-state";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { PLAYER_COLORS, playerColorName } from "@/shared/lib/player-colors";
import { loadColorPreference } from "@/shared/lib/player-color-preference";
import { queryKeys } from "@/shared/lib/queryKeys";
import { formatMoney } from "@/shared/lib/utils/format";
import { toCentsString } from "@/shared/lib/utils/display";
import { LoadingPage } from "@/pages/loading";
import type { RoomPlayer, SimulationData } from "@/types";
import { useJoinMatch } from "../hooks/useJoinMatch";
import { useMatchPlayers } from "../hooks/useMatchPlayers";

/** Tela de quem chegou com a partida em andamento: escolhe uma cor que sobrou e entra jogando. */
export function JoinMatchPage() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const { data: players, isLoading, error, refetch } = useMatchPlayers();

  // Quando a partida acaba, quem estava esperando entra na sala do lobby
  useRealtime("simulation_ended", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.authSession() });
  });

  if (isLoading || !simulation?.simulation) {
    return <LoadingPage variant="fullscreen" />;
  }

  if (!players) {
    return (
      <section className="flex min-h-svh items-center justify-center p-6">
        <Card className="w-full max-w-105">
          <CardContent>
            <ErrorState
              title="Não deu pra carregar a partida"
              description="O servidor do host não respondeu. Confira se ele está ligado e na mesma rede."
              error={error}
              onRetry={() => void refetch()}
            />
          </CardContent>
        </Card>
      </section>
    );
  }

  return <JoinMatchContent match={simulation.simulation} players={players} />;
}

type JoinMatchContentProps = {
  match: SimulationData;
  /** Quem joga a partida, com a cor de cada um */
  players: RoomPlayer[];
};

function JoinMatchContent({ match, players }: JoinMatchContentProps) {
  const { logout } = useAuth();
  const { data: online } = useRoomPlayers();
  const { mutate: join, isPending, error, reset } = useJoinMatch();
  const [choice, setChoice] = useState<string | null>(null);
  // Em equipes a escolha é obrigatória e não tem padrão: quem entra decide em qual equipe joga
  const inTeams = match.player_grouping === "TEAMS";
  const [team, setTeam] = useState<number | null>(null);

  const isFree = (color: string | null): color is string => color !== null && !players.some((p) => p.color === color);
  const firstFree = PLAYER_COLORS.find((c) => isFree(c.key))?.key;
  // A escolha vale enquanto estiver livre; senão a preferência do navegador, senão a primeira livre
  const preferred = loadColorPreference();
  const selected = isFree(choice) ? choice : isFree(preferred) ? preferred : firstFree;

  const onlineNicknames = new Set((online ?? []).map((p) => p.nickname));

  return (
    <section className="flex min-h-svh items-center justify-center p-6">
      <Card size="lg" className="w-full max-w-[460px]">
        <CardHeader>
          <CardTitle role="heading" aria-level={1}>
            Entrar na partida
          </CardTitle>
          <CardDescription>
            {match.name} já está em andamento. Escolha uma cor{inTeams ? " e uma equipe" : ""} e comece a jogar com o saldo inicial de{" "}
            <span className="font-mono">{formatMoney(toCentsString(match.starting_cash))}</span>.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="grid gap-5">
            {/* Jogadores da partida */}
            <div className="grid gap-2">
              <span className="text-xs font-semibold text-muted-foreground">
                Quem joga ({players.length} de {PLAYER_COLORS.length})
              </span>
              <div className="grid grid-cols-2 gap-2">
                {players.map((player) => {
                  const isOnline = onlineNicknames.has(player.nickname);
                  return (
                    <div
                      key={player.nickname}
                      className="flex items-center gap-2.5 rounded-[10px] border border-border p-2.5"
                    >
                      <PlayerAvatar nickname={player.nickname} color={player.color} />
                      <div className="grid min-w-0 flex-1">
                        <span className="truncate text-sm font-semibold">{player.nickname}</span>
                        <Status status={isOnline ? "online" : "offline"}>{isOnline ? "Online" : "Offline"}</Status>
                      </div>
                      {inTeams && <TeamBadge team={player.team} naming={match.team_naming} form="icon" />}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Escolha da cor */}
            <div className="grid gap-2">
              <span className="text-xs font-semibold text-muted-foreground">
                Sua cor{selected ? `: ${playerColorName(selected)}` : ""}
              </span>
              <PlayerColorGrid
                owners={players}
                selected={selected}
                disabled={isPending}
                onSelect={(color) => {
                  reset();
                  setChoice(color);
                }}
              />
            </div>

            {/* Escolha da equipe */}
            {inTeams && (
              <div className="grid gap-2">
                <span className="text-xs font-semibold text-muted-foreground">Sua equipe</span>
                <TeamGrid
                  players={players}
                  naming={match.team_naming}
                  selected={team}
                  disabled={isPending}
                  onSelect={(next) => {
                    reset();
                    setTeam(next);
                  }}
                />
              </div>
            )}

            {error && (
              <Alert variant="warning">
                <TriangleAlert />
                <AlertTitle>{error.message}</AlertTitle>
                <AlertDescription>Escolha outra cor livre{inTeams ? " e confira a equipe" : ""}.</AlertDescription>
              </Alert>
            )}

            <div className="grid gap-2">
              <Button
                size="lg"
                disabled={!selected || isPending || (inTeams && team === null)}
                onClick={() => selected && join({ color: selected, team: team ?? undefined })}
              >
                {isPending ? <Spinner /> : <DoorOpen />}
                Entrar na partida
              </Button>
              <Button variant="outline" disabled={isPending} onClick={() => void logout()}>
                Sair
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
