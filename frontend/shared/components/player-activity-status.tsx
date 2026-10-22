import { Status } from "@/shared/components/ui/status";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { PLAYER_ACTIVITIES } from "@/shared/lib/player-activity";
import type { RoomPlayer } from "@/types";

type PlayerActivityStatusProps = {
  /** O que o jogador está fazendo; nulo é "Online" (partida em andamento ou sem aviso ainda) */
  activity: RoomPlayer["activity"];
};

/** Selo de presença de quem está na sala: a tela em que está, com a frase inteira na dica. */
export function PlayerActivityStatus({ activity }: PlayerActivityStatusProps) {
  if (!activity) return <Status status="online">Online</Status>;

  const { label, hint } = PLAYER_ACTIVITIES[activity];
  return (
    <Tooltip>
      <TooltipTrigger render={<Status status={activity === "away" ? "away" : "online"} />}>{label}</TooltipTrigger>
      <TooltipContent side="top">{hint}</TooltipContent>
    </Tooltip>
  );
}
