import type { CandleChallengeState, CandleChallengeView, ChallengeDirection, ChallengePlayer } from "@/types";

/**
 * Aplica o estado que chegou pelo tempo real. O lado que o jogador escolheu só vale para a
 * pergunta em que ele respondeu: outra pergunta, ou a revelação, o apaga.
 */
export function withState(prev: CandleChallengeView | undefined, state: CandleChallengeState): CandleChallengeView {
  const sameQuestion = !!prev && !!state.question && prev.state.question?.id === state.question.id;
  return { state, direction: prev && sameQuestion ? prev.direction : null };
}

export function withDirection(
  prev: CandleChallengeView | undefined,
  direction: ChallengeDirection | null,
): CandleChallengeView | undefined {
  return prev && { ...prev, direction };
}

export function findPlayer(state: CandleChallengeState, nickname: string | undefined) {
  return state.players.find((player) => player.nickname === nickname);
}

/** Quem entrou com a pergunta já aberta e só joga a partir da próxima. */
export function isWatching(state: CandleChallengeState, player: ChallengePlayer | undefined) {
  return !!player && player.answered === 0 && player.joined_at > state.number;
}

/** Quantos dos que jogam esta pergunta já responderam. */
export function repliedCount(state: CandleChallengeState) {
  const playing = state.players.filter((player) => !isWatching(state, player));
  return { replied: playing.filter((player) => player.replied).length, playing: playing.length };
}

/** `declined` é o convite recusado (não volta nesta rodada); `closed` é quem fechou a janela e ainda pode entrar. */
export type WindowMode = "open" | "minimized" | "closed" | "declined";

/** O que o jogador fez com a janela vale só para a rodada em que fez: outra rodada abre de novo. */
export interface WindowChoice {
  round: number;
  mode: WindowMode;
}

export function windowMode(choice: WindowChoice | null, state: CandleChallengeState): WindowMode {
  return choice?.round === state.round_id ? choice.mode : "open";
}
