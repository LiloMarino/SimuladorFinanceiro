import { useState, type CSSProperties } from "react";
import { useMutation } from "@tanstack/react-query";
import { ChevronDown, Lock, Shield, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/shared/components/ui/popover";
import { TeamGrid } from "@/shared/components/team-grid";
import { teamColor, teamName, teamShortName } from "@/shared/lib/teams";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { RoomPlayer, TeamNaming } from "@/types";

type LobbyTeamPickerProps = {
  nickname: string;
  /** Quem está na sala agora, com a equipe de cada um */
  players: RoomPlayer[];
  /** Quem jogou a partida salva selecionada: a equipe deles fica guardada */
  savedPlayers: RoomPlayer[];
  naming: TeamNaming;
  /** Nome da partida salva selecionada, quando há */
  simulationName?: string;
};

/** "Sua equipe na partida": 10 equipes com os membros; a vazia abre uma nova. */
export function LobbyTeamPicker({ nickname, players, savedPlayers, naming, simulationName }: LobbyTeamPickerProps) {
  const [refusal, setRefusal] = useState<string | null>(null);

  const mine = players.find((p) => p.nickname === nickname)?.team;
  // Quem jogou a partida selecionada volta com a equipe dela
  const locked = savedPlayers.some((p) => p.nickname === nickname);
  const joiningNew = savedPlayers.length > 0 && !locked;

  // Quem muda a lista é o evento player_team
  const { mutate, isPending } = useMutation({
    mutationFn: (team: number) => apiFetch<void>("/api/simulation/players/me/team", { method: "PUT", body: { team } }),
  });
  const chooseTeam = (team: number) =>
    mutate(team, { onSuccess: () => setRefusal(null), onError: (err) => setRefusal(err.message) });

  return (
    <Popover onOpenChange={() => setRefusal(null)}>
      <PopoverTrigger render={<Button variant="outline" size="sm" />}>
        {mine ? (
          <>
            <Shield
              className="fill-(--team) stroke-(--team)"
              style={{ "--team": teamColor(mine) } as CSSProperties}
              aria-hidden="true"
            />
            {teamShortName(mine, naming)}
          </>
        ) : (
          "Escolher equipe"
        )}
        {locked ? <Lock className="text-muted-foreground" /> : <ChevronDown />}
      </PopoverTrigger>
      <PopoverContent align="end" className="w-96">
        <PopoverHeader>
          <PopoverTitle>{locked && simulationName ? `Sua equipe em ${simulationName}` : "Sua equipe na partida"}</PopoverTitle>
          <PopoverDescription>
            {locked
              ? `Você jogou esta partida na ${mine ? teamName(mine, naming) : "equipe dela"}. A equipe fica com a partida salva, como a cor.`
              : joiningNew && simulationName
                ? `Você entra em ${simulationName} como jogador novo. Escolha uma equipe antes de entrar.`
                : "Entre numa equipe com gente ou abra uma vazia. A cor é da equipe; a sua continua sendo a sua."}
          </PopoverDescription>
        </PopoverHeader>

        <TeamGrid players={players} naming={naming} selected={mine} disabled={locked || isPending} onSelect={chooseTeam} />

        {refusal && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertTitle>{refusal}</AlertTitle>
            {mine && <AlertDescription>Você continua na {teamName(mine, naming)}.</AlertDescription>}
          </Alert>
        )}
      </PopoverContent>
    </Popover>
  );
}
