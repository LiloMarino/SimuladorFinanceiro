import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";

/** Os avisos do desafio para a sala: quem entrou e o que aconteceu quando a partida começou. */
export function useCandleChallengeNotices() {
  useRealtime("candle_challenge_notice", ({ kind, nickname, number }) => {
    if (kind === "joined") {
      toast.info(`${nickname} entrou no desafio`, { description: "Joga a partir da próxima pergunta." });
    } else if (kind === "ended_by_match") {
      toast.info("O desafio da vela foi encerrado", {
        description: `A partida começou na pergunta ${number}. Os acertos já contam para as conquistas.`,
      });
    } else {
      toast.error("Não deu pra sortear uma pergunta", {
        description: "A base de preços não tem recortes que sirvam. O desafio foi encerrado.",
      });
    }
  });
}
