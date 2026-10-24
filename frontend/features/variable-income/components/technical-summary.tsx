import { AlertCircle } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { MetricHint } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { displayList, displayShortDate } from "@/shared/lib/utils/display";
import type { IndicatorParams, TechnicalReading, TechnicalSummary as Summary } from "@/types";
import {
  READING_HINT,
  SIGNAL_LABELS,
  SUMMARY_HINT,
  VERDICT_LABELS,
  displayReading,
  readingName,
  readingRule,
  readingWithArticle,
  summaryUnlock,
} from "../lib/indicators";

type Verdict = NonNullable<Summary["verdict"]>;

const VERDICT_TONE: Record<Verdict, string> = {
  strong_buy: "text-success",
  buy: "text-success",
  neutral: "text-muted-foreground",
  sell: "text-destructive",
  strong_sell: "text-destructive",
};

const SIGNAL_BADGE = {
  buy: "success",
  neutral: "secondary",
  sell: "destructive",
  none: "outline",
} as const satisfies Record<TechnicalReading["signal"], string>;

interface TechnicalSummaryProps {
  summary: Summary | undefined;
  params: IndicatorParams;
  status: "pending" | "error" | "success";
  onRetry: () => void;
}

/** A leitura de cada indicador no dia, a contagem e o ponteiro de Venda forte a Compra forte. */
export function TechnicalSummary({ summary, params, status, onRetry }: TechnicalSummaryProps) {
  return (
    <Card>
      {/* Cabeçalho */}
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1.5">
            Resumo técnico
            <MetricHint metric={SUMMARY_HINT} />
          </span>
        </CardTitle>
        {summary?.date && (
          <CardAction>
            <span className="text-xs text-muted-foreground">
              Fechamento de {displayShortDate(summary.date)} · regras fixas, não é previsão
            </span>
          </CardAction>
        )}
      </CardHeader>

      <CardContent>
        {status === "pending" && !summary ? (
          <Skeleton className="h-44" />
        ) : status === "error" && !summary ? (
          <div className="grid justify-items-start gap-2">
            <p className="flex items-start gap-2 text-[13px]">
              <AlertCircle className="size-4 shrink-0 text-destructive" />
              Sem leitura hoje: os indicadores não carregaram.
            </p>
            <Button variant="outline" size="sm" onClick={onRetry}>
              Tentar de novo
            </Button>
          </div>
        ) : summary ? (
          <SummaryBody summary={summary} params={params} />
        ) : null}
      </CardContent>
    </Card>
  );
}

function SummaryBody({ summary, params }: { summary: Summary; params: IndicatorParams }) {
  const prices = summary.readings.filter((reading) => reading.group === "price");
  const oscillators = summary.readings.filter((reading) => reading.group === "oscillator");
  return (
    <div className="grid items-start gap-5 md:grid-cols-[190px_minmax(0,1fr)_minmax(0,1fr)]">
      {/* Ponteiro e veredito */}
      {summary.verdict && summary.score !== null ? (
        <div className="grid justify-items-center gap-0.5">
          <Gauge score={summary.score} />
          <span className={cn("text-xl font-bold", VERDICT_TONE[summary.verdict])}>
            {VERDICT_LABELS[summary.verdict]}
          </span>
          <span className="text-center text-xs text-muted-foreground">
            {summary.buys} de {summary.counted} apontam compra · {summary.sells} venda
            {summary.sells === 1 ? "" : "s"}
          </span>
        </div>
      ) : (
        <div className="grid gap-1">
          <span className="text-lg font-bold text-muted-foreground">Ainda sem leitura</span>
          <span className="text-xs text-muted-foreground">
            <NotEnoughHistory summary={summary} />
          </span>
        </div>
      )}

      {/* Médias e faixa × osciladores */}
      <ReadingColumn title="Médias e faixa" readings={prices} params={params} />
      <ReadingColumn title="Osciladores" readings={oscillators} params={params} />
    </div>
  );
}

/** Quem já tem valor e qual indicador destrava o resumo, pelo nome. */
function NotEnoughHistory({ summary }: { summary: Summary }) {
  const ready = summary.readings.filter((reading) => reading.key !== "atr" && reading.value !== null);
  const unlock = summaryUnlock(summary);
  const verb = summary.counted === 1 ? "tem" : "têm";
  return (
    <>
      Só {summary.counted} de {summary.sided} indicadores {verb} pregões suficientes
      {ready.length > 0 && ` (${displayList(ready.map(readingWithArticle))})`}. O resumo aparece quando a maioria tiver
      {unlock && `: a partir do ${unlock.needed_sessions}º pregão, por causa d${readingWithArticle(unlock)}`}.
    </>
  );
}

function ReadingColumn({
  title,
  readings,
  params,
}: {
  title: string;
  readings: TechnicalReading[];
  params: IndicatorParams;
}) {
  const counted = readings.filter((reading) => reading.key !== "atr" && reading.value !== null);
  const buys = counted.filter((reading) => reading.signal === "buy").length;
  return (
    <div className="grid content-start gap-1.5">
      <div className="flex items-baseline justify-between">
        <span className="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">{title}</span>
        <span className="text-xs text-muted-foreground">
          {buys} de {counted.length} compra
        </span>
      </div>
      <div>
        {readings.map((reading) => (
          <ReadingRow key={reading.key} reading={reading} params={params} />
        ))}
      </div>
    </div>
  );
}

function ReadingRow({ reading, params }: { reading: TechnicalReading; params: IndicatorParams }) {
  const missing = reading.value === null;
  return (
    <Tooltip>
      <TooltipTrigger render={<div />}>
        <div className="grid grid-cols-[minmax(0,1fr)_auto_74px] items-center gap-x-2 border-t py-1.5 text-[13px]">
          <span className="flex min-w-0 items-center gap-1 font-medium whitespace-nowrap">
            {readingName(reading)}
            <MetricHint metric={READING_HINT[reading.key]} />
          </span>
          <span className="text-right font-mono text-xs tabular-nums">{displayReading(reading)}</span>
          {missing ? (
            <span />
          ) : (
            <Badge variant={SIGNAL_BADGE[reading.signal]} size="sm" className="justify-self-end">
              {SIGNAL_LABELS[reading.signal]}
            </Badge>
          )}
          <span className="col-span-3 truncate text-xs text-muted-foreground">
            {missing ? `faltam ${reading.missing_sessions} pregões` : reading.reason}
          </span>
        </div>
      </TooltipTrigger>
      <TooltipContent side="left" className="max-w-72">
        <b>A regra do {reading.label}</b>
        <p>{readingRule(reading, params)}</p>
        {!missing && (
          <p className="opacity-75">
            Hoje: {displayReading(reading)}, {reading.reason}.
          </p>
        )}
      </TooltipContent>
    </Tooltip>
  );
}

const SEGMENTS = [
  { token: "--destructive" },
  { token: "--destructive-soft" },
  { token: "--muted" },
  { token: "--success-soft" },
  { token: "--success" },
] as const;

/** Meia-lua de Venda forte (esquerda) a Compra forte (direita), com o ponteiro na nota. */
function Gauge({ score }: { score: number }) {
  const cx = 100;
  const cy = 100;
  const radius = 80;
  const point = (fraction: number, r: number) => {
    const angle = Math.PI * (1 - fraction);
    return [cx + r * Math.cos(angle), cy - r * Math.sin(angle)] as const;
  };
  // As faixas da nota: −1, −0,5, −0,2, 0,2, 0,5, 1
  const edges = [-1, -0.5, -0.2, 0.2, 0.5, 1].map((value) => (value + 1) / 2);
  const [needleX, needleY] = point((score + 1) / 2, radius - 14);
  return (
    <svg width={200} height={110} viewBox="0 0 200 110" role="img" aria-label="Ponteiro do resumo técnico">
      {SEGMENTS.map((segment, i) => {
        const [x1, y1] = point(edges[i], radius);
        const [x2, y2] = point(edges[i + 1], radius);
        return (
          <path
            key={segment.token}
            d={`M ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2}`}
            fill="none"
            stroke={`var(${segment.token})`}
            strokeWidth={14}
          />
        );
      })}
      <line
        x1={cx}
        y1={cy}
        x2={needleX}
        y2={needleY}
        stroke="var(--foreground)"
        strokeWidth={3}
        strokeLinecap="round"
      />
      <circle cx={cx} cy={cy} r={5} fill="var(--foreground)" />
      <text x={20} y={108} fontSize={10} textAnchor="middle" fill="var(--muted-foreground)">
        Venda
      </text>
      <text x={180} y={108} fontSize={10} textAnchor="middle" fill="var(--muted-foreground)">
        Compra
      </text>
    </svg>
  );
}
