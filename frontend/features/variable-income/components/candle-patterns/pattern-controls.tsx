import { AlertCircle, ChartCandlestick, Info } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { CandlePatternCode } from "@/types";
import { PATTERN_INFO } from "../../lib/candle-patterns";

interface PatternSwitchProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}

/** O interruptor "Padrões de vela" do topo do gráfico. */
export function PatternSwitch({ checked, onCheckedChange }: PatternSwitchProps) {
  return (
    <div className="inline-flex h-8 items-center gap-2 whitespace-nowrap rounded-lg border border-input bg-card px-2.5 text-[13px] font-medium">
      <Label htmlFor="candle-patterns-switch">Padrões de vela</Label>
      <Switch id="candle-patterns-switch" size="sm" checked={checked} onCheckedChange={onCheckedChange} />
      <span className="inline-flex text-faint-foreground">
        <Tooltip>
          <TooltipTrigger render={<Info className="size-3.5" aria-label="O que são padrões de vela" />} />
          <TooltipContent>
            Formas de vela que costumam anteceder uma alta ou uma baixa. São dicas do histórico, não promessas.
          </TooltipContent>
        </Tooltip>
      </span>
    </div>
  );
}

export type PatternNoticeProps =
  | { kind: "line"; count: number; todayCode: CandlePatternCode | null; onSeeCandles: () => void }
  | {
      kind: "empty";
      from: string | null;
      to: string;
      suggestion: { label: string; count: number } | null;
      onSuggest: () => void;
    }
  | { kind: "error"; onRetry: () => void };

/** Os avisos de padrões acima do gráfico: no gráfico de linha, sem padrão no período e erro. */
export function PatternNotice(props: PatternNoticeProps) {
  if (props.kind === "error") {
    return (
      <Alert variant="warning">
        <AlertCircle />
        <AlertDescription>
          <div className="flex flex-wrap items-center gap-3">
            <span className="flex-1">Não deu para carregar os padrões de vela.</span>
            <Button variant="outline" size="sm" onClick={props.onRetry}>
              Tentar de novo
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  const text =
    props.kind === "line" ? (
      <>
        <b className="font-mono">{props.count}</b> {props.count === 1 ? "padrão de vela neste período" : "padrões de vela neste período"}
        {props.todayCode && `, entre eles ${PATTERN_INFO[props.todayCode].name.toLowerCase()} hoje`}
      </>
    ) : (
      <>
        Nenhum padrão de vela entre {props.from === null ? "o início" : displayDayMonth(props.from)} e{" "}
        {displayDayMonth(props.to)}.
        {props.suggestion && (
          <>
            {" "}
            Em {props.suggestion.label} há <b className="font-mono">{props.suggestion.count}</b>.
          </>
        )}
      </>
    );
  const action =
    props.kind === "line" ? (
      <Button variant="outline" size="sm" onClick={props.onSeeCandles}>
        Ver em velas
      </Button>
    ) : props.suggestion ? (
      <Button variant="outline" size="sm" onClick={props.onSuggest}>
        Ver {props.suggestion.label}
      </Button>
    ) : null;

  return (
    <Alert variant="info">
      <ChartCandlestick />
      <AlertDescription>
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex-1 text-foreground">{text}</span>
          {action}
        </div>
      </AlertDescription>
    </Alert>
  );
}
