import { useState, type ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Spinner } from "@/shared/components/ui/spinner";
import { MetricHint } from "@/shared/components/metric-hint";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { CorrelationAssets, CorrelationWindow } from "@/types";
import { useCorrelation } from "../hooks/queries/useCorrelation";
import { COMMON_DAYS, CORRELATION, READING_BANDS, WINDOWS } from "../lib/correlation";
import { CorrelationHeatmap } from "./correlation-heatmap";
import { TickerPicker } from "./ticker-picker";

interface CorrelationToolProps {
  tickers: CorrelationAssets["tickers"];
  lastDate: NonNullable<CorrelationAssets["last_date"]>;
  endFixed: CorrelationAssets["end_fixed"];
}

const showDate = (iso: string) => displayDate(parseLocalDate(iso));

export function CorrelationTool({ tickers, lastDate, endFixed }: CorrelationToolProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const [period, setPeriod] = useState<CorrelationWindow>("1y");
  const [end, setEnd] = useState(lastDate);

  // Na partida, o backend fecha a janela na data da simulação
  const { data, isLoading, error } = useCorrelation(selected, period, endFixed ? null : end);

  const toggle = (ticker: string) =>
    setSelected((prev) => (prev.includes(ticker) ? prev.filter((t) => t !== ticker) : [...prev, ticker]));

  const renderMatrix = () => {
    if (selected.length === 0) return <Placeholder>Selecione ativos na lista para ver a correlação.</Placeholder>;
    if (isLoading) {
      return (
        <Placeholder>
          <Spinner className="size-6" />
        </Placeholder>
      );
    }
    if (error || !data) return <Placeholder>Erro ao calcular a correlação.</Placeholder>;
    return (
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">
          Retornos diários de {showDate(data.start)} a {showDate(data.end)}
        </p>
        <CorrelationHeatmap matrix={data} />
      </div>
    );
  };

  return (
    <div className="flex h-full flex-col md:flex-row">
      <TickerPicker tickers={tickers} selected={selected} onToggle={toggle} />

      <section className="min-w-0 flex-1 space-y-4 p-4">
        {/* Controles */}
        <div className="flex flex-wrap items-end gap-4">
          <div className="space-y-1">
            <Label htmlFor="correlation-window">Janela</Label>
            <Select value={period} onValueChange={(value) => setPeriod(value as CorrelationWindow)}>
              <SelectTrigger id="correlation-window" className="w-36">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {WINDOWS.map((w) => (
                  <SelectItem key={w.value} value={w.value}>
                    {w.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label htmlFor="correlation-end">{endFixed ? "Termina na data da simulação" : "Termina em"}</Label>
            <Input
              id="correlation-end"
              type="date"
              className="w-44"
              value={endFixed ? lastDate : end}
              max={lastDate}
              disabled={endFixed}
              onChange={(e) => e.target.value && setEnd(e.target.value)}
            />
          </div>
        </div>

        <div className="grid gap-4 xl:grid-cols-[1fr_20rem]">
          {/* Mapa de calor */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-1">
                {CORRELATION.label}
                <MetricHint metric={CORRELATION} />
              </CardTitle>
              <CardDescription>{CORRELATION.description}. O Ibovespa entra como referência.</CardDescription>
            </CardHeader>
            <CardContent>{renderMatrix()}</CardContent>
          </Card>

          {/* Como ler */}
          <Card>
            <CardHeader>
              <CardTitle>Como ler</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>{CORRELATION.reading}</p>
              <ul className="space-y-1">
                {READING_BANDS.map((band, i) => (
                  <li key={band.label} className="flex justify-between gap-2">
                    <span className="tabular-nums text-muted-foreground">{bandRange(i)}</span>
                    <span className="text-right">{band.label}</span>
                  </li>
                ))}
              </ul>
              <div className="space-y-1 border-t pt-3">
                <p className="flex items-center gap-1 font-medium">
                  {COMMON_DAYS.label}
                  <MetricHint metric={COMMON_DAYS} />
                </p>
                <p className="text-muted-foreground">
                  {COMMON_DAYS.description}: aparece ao passar o mouse em cada célula. Com poucos pregões em comum, a
                  célula fica com "—".
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}

/** Intervalo da faixa `i` de READING_BANDS, como "0,3 a 0,7". */
function bandRange(i: number) {
  const fmt = (n: number) => n.toLocaleString("pt-BR").replace("-", "−");
  const min = READING_BANDS[i].min;
  const max = i === 0 ? 1 : READING_BANDS[i - 1].min;
  return `${min === -Infinity ? "−1" : fmt(min)} a ${fmt(max)}`;
}

function Placeholder({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-72 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
      {children}
    </div>
  );
}
