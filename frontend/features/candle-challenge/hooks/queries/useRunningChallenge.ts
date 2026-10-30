import { useCandleChallenge } from "./useCandleChallenge";

/** O número da pergunta em que o desafio da vela está, ou `null` quando nenhum rola. */
export function useRunningChallenge() {
  const { data } = useCandleChallenge();
  return data?.state.status === "running" ? Math.min(data.state.number, data.state.total) : null;
}
