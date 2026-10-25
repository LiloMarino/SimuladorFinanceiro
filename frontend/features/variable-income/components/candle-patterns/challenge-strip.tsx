import type { ReactNode } from "react";
import { ChartCandlestick } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { CandleChallenge, ChallengeAnswer, ChallengeDirection } from "@/types";
import { PATTERN_INFO } from "../../lib/candle-patterns";
import { hitRate, sideWord } from "../../lib/pattern-view";

interface ChallengeStripProps {
  challenge: CandleChallenge;
  /** A resposta a mostrar (a última, se ainda recente); a pergunta aberta tem prioridade. */
  answer: ChallengeAnswer | null;
  pending: boolean;
  onAnswer: (direction: ChallengeDirection) => void;
}

/** O desafio da vela entre a legenda e o gráfico: pergunta, espera ou resultado, e o placar à direita. */
export function ChallengeStrip({ challenge, answer, pending, onAnswer }: ChallengeStripProps) {
  const { open, score } = challenge;
  const scoreText = (
    <span className="text-xs whitespace-nowrap text-muted-foreground">
      Seu placar{" "}
      <b className="font-mono text-foreground">
        {score.hits} de {score.answered}
      </b>
    </span>
  );

  if (open) {
    const info = PATTERN_INFO[open.pattern_code];
    return (
      <Alert>
        <ChartCandlestick />
        <AlertDescription>
          <div className="flex flex-wrap items-center gap-3">
            <div className="grid min-w-0 flex-1 gap-0.5">
              <span className="text-[13px] font-semibold text-foreground">
                Desafio da vela · {info.name} hoje. E agora, sobe ou desce?
              </span>
              <span className="text-xs">
                Conferimos no fechamento de {displayDayMonth(open.settles_on)}, daqui a 5 pregões. Responda até o
                próximo pregão.
              </span>
            </div>
            <Button variant="outline-success" size="sm" disabled={pending} onClick={() => onAnswer("up")}>
              ▲ Sobe
            </Button>
            <Button variant="outline-destructive" size="sm" disabled={pending} onClick={() => onAnswer("down")}>
              ▼ Desce
            </Button>
            {scoreText}
          </div>
        </AlertDescription>
      </Alert>
    );
  }
  if (!answer) return null;

  const { title, detail, variant } = describeAnswer(answer);
  return (
    <Alert variant={variant}>
      <ChartCandlestick />
      <AlertDescription>
        <div className="flex flex-wrap items-center gap-3">
          <div className="grid min-w-0 flex-1 gap-0.5">
            <span
              className={cn(
                "text-[13px] font-semibold text-foreground",
                answer.status === "expired" && "text-muted-foreground",
              )}
            >
              {title}
            </span>
            <span className="text-xs">{detail}</span>
          </div>
          {scoreText}
        </div>
      </AlertDescription>
    </Alert>
  );
}

function describeAnswer(answer: ChallengeAnswer): {
  title: ReactNode;
  detail: ReactNode;
  variant: "default" | "muted" | "success" | "destructive";
} {
  const info = PATTERN_INFO[answer.pattern_code];
  const day = displayDayMonth(answer.pattern_date);
  const side = info.side === "neutral" ? null : info.side;
  const rate = hitRate(answer.stats);

  if (answer.status === "expired") {
    return {
      variant: "muted",
      title: `O desafio ${info.of} de ${day} passou`,
      detail: "Valia só até o pregão seguinte. Sem resposta, não conta no placar.",
    };
  }

  const change = answer.change === null ? "" : displaySignedPercent(answer.change, 1);

  if (answer.status === "waiting") {
    const up = answer.direction === "up";
    return {
      variant: "default",
      title: (
        <>
          Você respondeu ao desafio {info.of} de {day}:{" "}
          <span className={up ? "text-success" : "text-destructive"}>{up ? "▲ sobe" : "▼ desce"}</span>
        </>
      ),
      detail: (
        <>
          Fechou em {displayMoney(answer.price)} · conferimos em {displayDayMonth(answer.settles_on)} · faltam{" "}
          {answer.sessions_left} {answer.sessions_left === 1 ? "pregão" : "pregões"}. Hoje:{" "}
          <span className="font-mono">
            {displayMoney(answer.current_price ?? answer.price)} ({change})
          </span>
        </>
      ),
    };
  }

  if (answer.status === "void") {
    return {
      variant: "muted",
      title: `O preço fechou igual: o desafio ${info.of} foi anulado`,
      detail: "Pergunta anulada não conta no placar.",
    };
  }

  const path = `De ${displayMoney(answer.price)} em ${day} para ${displayMoney(answer.current_price ?? answer.price)} em ${displayDayMonth(answer.settles_on)} (${change}).`;
  const moved = (answer.change ?? 0) > 0 ? "subiu" : "caiu";
  if (answer.status === "hit") {
    return {
      variant: "success",
      title: `Acertou: o preço ${moved} depois ${info.of}`,
      detail: `${path} ${hitFootnote(rate, side, answer.direction)}`.trim(),
    };
  }
  return {
    variant: "destructive",
    title: `Não foi desta vez: o preço ${moved} depois ${info.of}`,
    detail: `${path} ${missFootnote(rate, side, info.name)}`.trim(),
  };
}

/** Lembra que padrão não é garantia: em quantas das vezes o outro lado ganhou. */
function hitFootnote(rate: number | null, side: "up" | "down" | null, direction: ChallengeDirection | null) {
  if (rate === null || side === null) return "";
  if (direction === side) {
    return `Nas outras ${Math.round((1 - rate) * 100)}% das vezes, teria ${side === "up" ? "caído" : "subido"}.`;
  }
  return `Você foi contra o padrão, que acerta ${Math.round(rate * 100)}% das vezes.`;
}

function missFootnote(rate: number | null, side: "up" | "down" | null, name: string) {
  if (rate === null || side === null) return "";
  return `O padrão (${name}) sugere ${sideWord(side)}, mas falha ${Math.round((1 - rate) * 10)} em cada 10 vezes.`;
}
