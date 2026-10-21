import { useAchievements } from "./useAchievements";

/** O placar do jogador ("9 de 24") e se há conquista que ele ainda não viu. */
export function useAchievementTally() {
  const { data } = useAchievements();
  if (!data) return undefined;

  return {
    unlocked: data.filter((a) => a.unlock).length,
    total: data.length,
    hasNew: data.some((a) => a.unlock?.is_new),
  };
}
