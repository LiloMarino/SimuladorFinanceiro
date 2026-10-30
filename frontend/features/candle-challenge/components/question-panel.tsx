import { Eye, Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import type { CandleChallengeState, ChallengeDirection, ChallengePlayer } from "@/types";
import { isWatching, repliedCount } from "../lib/view";
import { sideVerb } from "../lib/text";
import { CandleChart } from "./candle-chart";
import { PatternHint } from "./pattern-hint";
import { TimerBar } from "./timer-bar";
import { VoteButtons } from "./vote-buttons";

interface QuestionPanelProps {
  state: CandleChallengeState;
  me: ChallengePlayer | undefined;
  direction: ChallengeDirection | null;
  onVote: (direction: ChallengeDirection) => void;
  /** O gráfico mais baixo cabe no palco apertado (janela estreita). */
  chartHeight?: number;
}

/** A pergunta aberta: o recorte sem ativo nem data, o tempo e os botões de resposta. */
export function QuestionPanel({ state, me, direction, onVote, chartHeight = 380 }: QuestionPanelProps) {
  const question = state.question;
  if (!question) return null;
  const watching = isWatching(state, me);
  const { replied, playing } = repliedCount(state);

  return (
    <div className="grid gap-4">
      <div className="grid gap-1">
        <h2 className="text-xl leading-snug font-semibold">
          O recorte terminou num <PatternHint code={question.pattern_code} stats={question.stats} />. Nos próximos 5
          pregões, sobe ou desce?
        </h2>
        <p className="text-[13px] text-muted-foreground">
          Ativo e data ficam escondidos até a revelação. O eixo mostra quanto o preço andou desde a primeira vela.
        </p>
      </div>

      {watching && (
        <Alert variant="info">
          <Eye />
          <AlertTitle>Você entra na próxima pergunta</AlertTitle>
          <AlertDescription>
            Esta já estava aberta quando você chegou: dá para assistir, mas não vale ponto.
          </AlertDescription>
        </Alert>
      )}
      {direction && !watching && (
        <Alert variant="info">
          <Info />
          <AlertTitle>Você disse que {sideVerb(direction)}</AlertTitle>
          <AlertDescription>
            Dá para trocar até fechar. {replied} de {playing} já responderam.
          </AlertDescription>
        </Alert>
      )}

      <div className="rounded-xl border py-1.5">
        <CandleChart bars={question.bars} box={{ width: 770, height: chartHeight }} />
      </div>

      <TimerBar key={question.id} remainingMs={question.remaining_ms} durationMs={question.duration_ms} />
      <VoteButtons direction={direction} disabled={watching || !me} onVote={onVote} />
    </div>
  );
}
