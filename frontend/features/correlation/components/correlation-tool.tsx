import { useState } from "react";
import { Clock, Grid3x3, TriangleAlert } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { Input } from "@/shared/components/ui/input";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { MetricHint } from "@/shared/components/metric-hint";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { CorrelationAssets, CorrelationWindow } from "@/types";
import { useCorrelation } from "../hooks/queries/useCorrelation";
import { MAX_TICKERS, oneOfEachSector } from "../lib/assets";
import { CORRELATION, WINDOWS } from "../lib/correlation";
import { AssetPicker } from "./asset-picker";
import { CorrelationMatrixGrid, type PairPosition } from "./correlation-matrix";
import { CorrelationSidePanel } from "./correlation-side-panel";

interface CorrelationToolProps {
  assets: CorrelationAssets["assets"];
  lastDate: NonNullable<CorrelationAssets["last_date"]>;
  endFixed: CorrelationAssets["end_fixed"];
}

const showDate = (iso: string) => displayDate(parseLocalDate(iso));

export function CorrelationTool({ assets, lastDate, endFixed }: CorrelationToolProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const [period, setPeriod] = useState<CorrelationWindow>("1y");
  const [end, setEnd] = useState(lastDate);
  const [pinned, setPinned] = useState<PairPosition | null>(null);

  // A carteira só existe na partida, e é nela que a data fica travada
  const { data: portfolio } = usePortfolio({ enabled: endFixed });
  const tickers = new Set(assets.map((a) => a.ticker));
  const held = (portfolio?.variable_income ?? []).map((p) => p.ticker).filter((t) => tickers.has(t));

  // Na partida, o backend fecha a janela na data da simulação
  const { data, error, refetch } = useCorrelation(selected, period, endFixed ? null : end);

  // A posição do par fixado vale para uma seleção: mudou a lista, ele sai
  const replace = (next: string[]) => {
    setSelected(next);
    setPinned(null);
  };
  const toggle = (ticker: string) =>
    replace(selected.includes(ticker) ? selected.filter((t) => t !== ticker) : [...selected, ticker]);

  const renderMatrix = () => {
    if (selected.length < 2) {
      return (
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <Grid3x3 />
            </EmptyMedia>
            <EmptyTitle>Escolha pelo menos dois ativos</EmptyTitle>
            <EmptyDescription>
              Ou comece por um atalho: compare as ações que você já tem, ou uma de cada setor.
            </EmptyDescription>
          </EmptyHeader>
          <EmptyContent className="flex-row justify-center">
            {held.length >= 2 && (
              <Button variant="outline" onClick={() => replace(held.slice(0, MAX_TICKERS))}>
                Minha carteira
              </Button>
            )}
            <Button variant="outline" onClick={() => replace(oneOfEachSector(assets))}>
              Um de cada setor
            </Button>
          </EmptyContent>
        </Empty>
      );
    }
    if (!data) {
      return error ? (
        <ErrorState
          title="Não deu pra calcular agora"
          description="Confira se o servidor do host está ligado e tente de novo."
          error={error}
          onRetry={() => void refetch()}
        />
      ) : (
        <Skeleton className="h-72" />
      );
    }
    return (
      <div className="grid gap-4">
        {error && (
          <Alert variant="destructive">
            <TriangleAlert />
            <AlertTitle>Não deu pra calcular agora</AlertTitle>
            <AlertDescription>A matriz anterior continua valendo até o novo cálculo dar certo.</AlertDescription>
            <AlertAction>
              <Button variant="outline" size="sm" onClick={() => void refetch()}>
                Tentar de novo
              </Button>
            </AlertAction>
          </Alert>
        )}
        <CorrelationMatrixGrid matrix={data} pinned={pinned} onPin={setPinned} />
      </div>
    );
  };

  const matrixReady = selected.length >= 2 && data;

  return (
    <div className="grid gap-5">
      {/* Janela e data final */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-xs font-medium text-muted-foreground">Janela</span>
        <ToggleGroup
          variant="segmented"
          aria-label="Janela"
          value={[period]}
          onValueChange={(values) => values[0] && setPeriod(values[0] as CorrelationWindow)}
        >
          {WINDOWS.map((w) => (
            <ToggleGroupItem key={w.value} value={w.value}>
              {w.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
        {endFixed ? (
          <Badge variant="secondary">
            <Clock />
            <span className="font-mono">até {showDate(lastDate)}</span> · data da simulação
          </Badge>
        ) : (
          <label className="flex items-center gap-2 text-[13px] text-muted-foreground">
            até
            <Input
              type="date"
              value={end}
              max={lastDate}
              onChange={(e) => e.target.value && setEnd(e.target.value)}
              aria-label="Data final da janela"
            />
          </label>
        )}
      </div>

      <div className="grid items-start gap-5 lg:grid-cols-[260px_minmax(0,1fr)] xl:grid-cols-[260px_minmax(0,1fr)_300px]">
        <AssetPicker assets={assets} held={held} selected={selected} onToggle={toggle} onReplace={replace} />

        {/* Matriz */}
        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>
              <span className="flex items-center gap-1">
                Quanto andam juntos
                <MetricHint metric={CORRELATION} />
              </span>
            </CardTitle>
            <CardDescription>
              {data && matrixReady
                ? `Correlação dos retornos diários de ${showDate(data.start)} a ${showDate(data.end)}. Clique numa célula pra ver o par.`
                : CORRELATION.description}
            </CardDescription>
          </CardHeader>
          <CardContent>{renderMatrix()}</CardContent>
        </Card>

        {matrixReady && <CorrelationSidePanel matrix={data} pinned={pinned} />}
      </div>
    </div>
  );
}
