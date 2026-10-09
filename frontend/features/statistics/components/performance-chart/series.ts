import { stringToColor } from "@/shared/lib/utils";
import type { PlayerPerformance } from "@/types";
import { playerLabel } from "../../lib/player-label";

export interface PlayerSeries {
  key: string;
  label: string;
  color: string;
  defaultVisible: boolean;
}

export function buildPlayerSeries(players: PlayerPerformance[], showSimulation: boolean): PlayerSeries[] {
  return players.map((p) => {
    const label = playerLabel(p, showSimulation);
    return { key: label, label, color: stringToColor(label), defaultVisible: true };
  });
}
