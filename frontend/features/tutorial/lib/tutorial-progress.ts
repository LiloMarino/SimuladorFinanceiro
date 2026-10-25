import { matchPath } from "react-router-dom";
import type { RoomPlayer } from "@/types";
import type { Topic } from "./topics";
import type { TutorialState } from "./tutorial-storage";

export const isSeen = (state: TutorialState, topic: Pick<Topic, "id">) => state.seen.includes(topic.id);

/** Tópicos que o jogador ainda não abriu. */
export const unseenTopics = <T extends Pick<Topic, "id">>(state: TutorialState, topics: readonly T[]) =>
  topics.filter((topic) => !isSeen(state, topic));

/** O primeiro tópico da tela que ainda não foi visto nem avisado. */
export function nudgeTopicFor<T extends Pick<Topic, "id" | "screens">>(
  state: TutorialState,
  topics: readonly T[],
  pathname: string,
): T | undefined {
  return topics.find(
    (topic) =>
      !isSeen(state, topic) &&
      !state.nudged.includes(topic.id) &&
      topic.screens.some((pattern) => matchPath(pattern, pathname)),
  );
}

/** Jogadores de verdade da sala: os bots não pedem que o tempo espere. */
export const countHumans = (players: readonly Pick<RoomPlayer, "bot">[]) =>
  players.filter((player) => player.bot == null).length;

/** Abrir a janela pausa a partida só quando o jogador está sozinho e o tempo corre. */
export const shouldPause = (humans: number, speed: number) => humans === 1 && speed > 0;

/** Fechar retoma só o que a janela pausou, e só se ninguém mexeu na velocidade depois. */
export const shouldResume = (pausedByUs: boolean, speed: number) => pausedByUs && speed === 0;
