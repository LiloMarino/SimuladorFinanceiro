import { useMemo } from "react";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useHeirCapital } from "./queries/useHeirCapital";
import type { RoomHeir } from "../lib/minimum-goal";

/** O Herdeiro da sala, jogador ou bot, com o capital com que ele começa; nulo sem Herdeiro ou sem o capital. */
export function useRoomHeir(): RoomHeir | null {
  const { data: players } = useRoomPlayers();
  const { data: heirCapital } = useHeirCapital();

  const heir = players?.find((player) => player.profession === "HEIR");
  const nickname = heir?.nickname;
  const isBot = heir?.bot != null;
  const capital = heirCapital ? Number(heirCapital.starting_capital) : null;

  return useMemo(
    () => (nickname !== undefined && capital !== null ? { nickname, isBot, capital } : null),
    [nickname, isBot, capital],
  );
}
