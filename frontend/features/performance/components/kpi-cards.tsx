import type { ReactNode } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  displayBytes,
  displayDuration,
  displayNumber,
  displayPercent,
} from "@/shared/lib/utils/display";
import type { MetricsData } from "@/types";
import {
  engineStatus,
  httpSummary,
  SLOW_P95_MS,
  trafficSummary,
  type Row,
} from "../lib/stats";

interface KpiProps {
  label: string;
  value: ReactNode;
  unit?: string;
  note?: ReactNode;
  children?: ReactNode;
  tone?: "default" | "destructive";
}

function Kpi({
  label,
  value,
  unit,
  note,
  children,
  tone = "default",
}: KpiProps) {
  return (
    <Card
      size="sm"
      variant={tone === "destructive" ? "destructive" : "default"}
    >
      <CardContent>
        <div className="grid content-start gap-1.5">
          <span className="text-xs font-medium text-muted-foreground">
            {label}
          </span>
          <span className="font-mono text-[22px] leading-tight font-semibold">
            {value}
            {unit && (
              <span className="ml-1.5 font-sans text-[13px] font-medium text-muted-foreground">
                {unit}
              </span>
            )}
          </span>
          {note && (
            <span className="text-xs text-muted-foreground">{note}</span>
          )}
          {children}
        </div>
      </CardContent>
    </Card>
  );
}

interface EngineCardProps {
  data: MetricsData;
}

/** Quanto o motor leva por dia contra o tempo que cabe na velocidade pedida. */
export function EngineCard({ data }: EngineCardProps) {
  const { item, speed, budgetMs, late, effectiveSpeed } = engineStatus(data);

  if (!item) {
    return (
      <Kpi
        label="Ritmo do tempo · motor"
        value="—"
        note="Nenhum dia processado ainda. Dê play na partida."
      >
        <Badge variant="secondary" className="w-max">
          Sem medição
        </Badge>
      </Kpi>
    );
  }

  const fill = budgetMs ? Math.min(100, (item.mean_ms / budgetMs) * 100) : 0;
  const marker = budgetMs ? Math.min(100, (item.p95_ms / budgetMs) * 100) : 0;

  return (
    <Kpi
      label="Ritmo do tempo · motor"
      value={displayDuration(item.mean_ms)}
      unit="por dia"
      tone={late ? "destructive" : "default"}
      note={
        budgetMs
          ? `A ${speed}× cada dia tem ${displayDuration(budgetMs)}${late ? `: ${displayNumber(item.mean_ms / budgetMs, 1)} vezes o tempo que cabe` : ` · p95 em ${displayDuration(item.p95_ms)} (traço)`}`
          : "Partida pausada: sem tempo de referência"
      }
    >
      {budgetMs !== null && (
        <div
          className="relative mt-1 h-2 rounded-full bg-muted"
          role="img"
          aria-label="Tempo gasto contra o tempo que cabe"
        >
          <div
            className={`absolute inset-y-0 left-0 rounded-full ${late ? "bg-destructive" : "bg-primary"}`}
            style={{ width: `${fill}%` }}
          />
          <div
            className="absolute -top-1 h-4 w-0.5 rounded-sm bg-foreground"
            style={{ left: `${marker}%` }}
          />
        </div>
      )}
      {late && effectiveSpeed !== null ? (
        <Badge variant="destructive" className="w-max">
          Atrasando · roda a ~{effectiveSpeed}×
        </Badge>
      ) : (
        budgetMs !== null && (
          <Badge variant="success" className="w-max">
            Em dia · sobram {displayDuration(budgetMs - item.mean_ms)}
          </Badge>
        )
      )}
    </Kpi>
  );
}

function HttpCard({ data }: EngineCardProps) {
  const { calls, p95Ms, slowRoutes } = httpSummary(data);
  return (
    <Kpi
      label="Requisições HTTP"
      value={displayNumber(calls, 0)}
      note={
        p95Ms !== null
          ? `p95 geral de ${displayDuration(p95Ms)}`
          : "Nenhuma requisição medida"
      }
    >
      {slowRoutes > 0 ? (
        <Badge variant="destructive" className="w-max">
          {slowRoutes} {slowRoutes === 1 ? "rota lenta" : "rotas lentas"} (p95
          &gt; {SLOW_P95_MS} ms)
        </Badge>
      ) : (
        calls > 0 && (
          <Badge variant="success" className="w-max">
            Nenhuma rota lenta
          </Badge>
        )
      )}
    </Kpi>
  );
}

function TrafficCard({ data }: EngineCardProps) {
  const { msgsPerSecond, bytesPerSecond, top } = trafficSummary(data.traffic);
  return (
    <Kpi
      label="Enviado ao navegador · Socket.IO"
      value={data.traffic.length ? `${displayBytes(bytesPerSecond)}/s` : "—"}
      note={
        data.traffic.length
          ? `${displayNumber(msgsPerSecond, 0)} mensagens por segundo, para ${data.players} ${data.players === 1 ? "jogador" : "jogadores"}`
          : "Nada enviado ainda"
      }
    >
      {top && (
        <Badge
          variant={top.share >= 0.5 ? "warning" : "secondary"}
          className="w-max"
        >
          {displayPercent(top.share, 0)} é {top.event}
        </Badge>
      )}
    </Kpi>
  );
}

interface TopCardProps {
  rows: Row[];
  onSeeTable: () => void;
}

/** O que mais soma tempo, e o maior fora o motor (que costuma dominar a conta). */
function TopCard({ rows, onSeeTable }: TopCardProps) {
  const top = rows[0];
  const outsideEngine = rows.find((row) => row.kind !== "engine");

  return (
    <Kpi
      label="Onde mais vai tempo"
      value={
        <span className="font-sans text-lg leading-snug">
          {top ? top.label : "—"}
        </span>
      }
      note={
        top
          ? `${displayPercent(top.share, 0)} do tempo medido${top.kind === "engine" && outsideEngine ? ` · fora o motor: ${outsideEngine.label} (${displayPercent(outsideEngine.share, 0)})` : ""}`
          : "Nada medido ainda"
      }
    >
      {top && (
        <button
          type="button"
          onClick={onSeeTable}
          className="w-max text-[13px] font-medium text-primary hover:underline"
        >
          Ver na tabela ↓
        </button>
      )}
    </Kpi>
  );
}

interface KpiCardsProps {
  data: MetricsData;
  /** Linhas já ordenadas pelo tempo total. */
  rowsByTotal: Row[];
  onSeeTable: () => void;
}

export function KpiCards({ data, rowsByTotal, onSeeTable }: KpiCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <EngineCard data={data} />
      <HttpCard data={data} />
      <TrafficCard data={data} />
      <TopCard rows={rowsByTotal} onSeeTable={onSeeTable} />
    </div>
  );
}
