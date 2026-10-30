import { Flame, Minus } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import { displaySignedPercent } from "@/shared/lib/utils/display";
import type { CandleChallengeState, ChallengeDirection, ChallengePlayer, ChallengeReveal } from "@/types";
import { displayPeriod, verdictText } from "../lib/text";
import { isWatching } from "../lib/view";
import { CandleChart } from "./candle-chart";

interface RevealPanelProps {
  state: CandleChallengeState;
  me: ChallengePlayer | undefined;
  /** O que o jogador respondeu, tirado dos votos da revelação. */
  myVote: ChallengeDirection | undefined;
  chartHeight?: number;
}

/** O resultado da pergunta: primeiro em palavras e com a cor do lado certo, depois o ativo, a data e as 5 velas. */
export function RevealPanel({ state, me, myVote, chartHeight = 300 }: RevealPanelProps) {
  const reveal = state.reveal;
  if (!reveal) return null;
  const watching = isWatching(state, me);
  const period = displayPeriod(reveal.start, reveal.end);

  return (
    <div className="grid gap-3.5">
      {reveal.outcome === "void" ? (
        <Alert>
          <Minus />
          <AlertTitle>Ficou no mesmo preço: pergunta anulada</AlertTitle>
          <AlertDescription>
            Era {reveal.ticker}, {period}. Ninguém ganha nem perde ponto, e ela não conta entre as {state.total}.
          </AlertDescription>
        </Alert>
      ) : (
        <Verdict reveal={reveal} me={watching ? undefined : me} myVote={myVote} period={period} />
      )}
      <div className="rounded-xl border py-1.5">
        <CandleChart bars={reveal.bars} after={reveal.bars_after} box={{ width: 770, height: chartHeight }} />
      </div>
      {state.solo && state.streak > 0 && <StreakAlert streak={state.streak} record={state.record} />}
    </div>
  );
}

function Verdict({
  reveal,
  me,
  myVote,
  period,
}: {
  reveal: ChallengeReveal;
  me: ChallengePlayer | undefined;
  myVote: ChallengeDirection | undefined;
  period: string;
}) {
  const up = reveal.outcome === "up";
  return (
    <div
      className={cn(
        "grid grid-cols-[auto_1fr_auto] items-center gap-3.5 rounded-xl px-4 py-3.5",
        up ? "bg-success-soft" : "bg-destructive-soft",
      )}
    >
      <span
        className={cn(
          "grid size-11 place-items-center rounded-lg text-xl text-white",
          up ? "bg-success" : "bg-destructive",
        )}
        aria-hidden
      >
        {up ? "▲" : "▼"}
      </span>
      <div className="grid gap-0.5">
        <b className="text-lg">
          {up ? "Subiu" : "Desceu"} em 5 pregões{" "}
          <span className="font-mono">{displaySignedPercent(reveal.change, 1)}</span>
        </b>
        <span className="text-[13px]">
          Era <b>{reveal.ticker}</b>, {period}.{me && ` ${verdictText(myVote, me.last)}`}
        </span>
      </div>
      {me?.last === "hit" && (
        <Badge variant="success" size="status">
          +1 ponto
        </Badge>
      )}
    </div>
  );
}

function StreakAlert({ streak, record }: { streak: number; record: number }) {
  const missing = record - streak + 1;
  return (
    <Alert variant="warning">
      <Flame />
      <AlertTitle>
        {streak} {streak === 1 ? "seguida" : "seguidas"}
        {record > 0 && ` · seu recorde é ${record}`}
      </AlertTitle>
      {record > streak && (
        <AlertDescription>
          Mais {missing} {missing === 1 ? "acerto" : "acertos"} e você bate o recorde.
        </AlertDescription>
      )}
    </Alert>
  );
}
