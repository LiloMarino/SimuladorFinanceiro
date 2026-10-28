import { useMemo, useState } from "react";
import { LineChart as LineChartIcon } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useGoalSteps } from "@/shared/hooks/queries/useGoalSteps";
import { usePatrimonialHistory } from "@/shared/hooks/queries/usePatrimonialHistory";
import { displayMoney, displayPercent, displaySignedMoney } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";
import { useElementWidth } from "../hooks/useElementWidth";
import {
  isPeriodAvailable,
  PERIODS,
  pointsInPeriod,
  toNetworthPoints,
  type NetworthPoint,
  type Period,
} from "../lib/networth-model";
import { NetworthClassPanels } from "./networth-class-panels";
import { NetworthGainChart } from "./networth-gain-chart";

type Mode = "gain" | "class";

/** Evolução da carteira: o patrimônio de hoje e o gráfico em dois modos, ganho sobre o aportado ou um painel por classe. */
export function NetworthChart({ portfolio }: { portfolio: PortfolioState }) {
  const { data: history, isLoading, error, refetch } = usePatrimonialHistory();
  const goalSteps = useGoalSteps();
  const [period, setPeriod] = useState<Period>("ALL");
  const [mode, setMode] = useState<Mode>("gain");
  const [attachWidth, width] = useElementWidth<HTMLDivElement>();

  const all = useMemo(() => toNetworthPoints(history ?? [], goalSteps), [history, goalSteps]);
  const points = useMemo(() => pointsInPeriod(all, period), [all, period]);

  const title = (
    <CardTitle>
      <span className="flex items-center gap-1.5">
        Evolução do patrimônio
        <InfoHint label="Como ler este gráfico">
          <div className="grid gap-2 text-left text-xs leading-snug">
            <b className="text-[13px]">Como ler este gráfico</b>
            <span>
              <b>Patrimônio</b> é o que você tem (caixa, renda fixa e ações) menos o que deve no Crédito.
            </span>
            <span>
              <b>Aportado</b> é o que saiu do seu bolso: o dinheiro inicial mais os aportes.
            </span>
            <span>
              <b>Ganho</b> é a diferença. Ex.: aportou R$ 95.000 e tem R$ 123.255, ganhou R$ 28.255, que são 29,7% sobre
              o aportado.
            </span>
            <span className="text-muted-foreground">Acima de 0% o dinheiro rendeu; abaixo, encolheu.</span>
          </div>
        </InfoHint>
      </span>
    </CardTitle>
  );

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <div className="grid gap-3">
            <div className="flex items-start justify-between">
              <div className="grid gap-2">
                <Skeleton className="h-4 w-44" />
                <Skeleton className="h-5.5 w-60" />
              </div>
              <Skeleton className="h-7.5 w-29" />
            </div>
            <Skeleton className="h-42.5" />
            <Skeleton className="h-3 w-64" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!history) {
    return (
      <Card>
        <CardHeader>{title}</CardHeader>
        <CardContent>
          <ErrorState
            title="Não deu pra carregar o histórico"
            description="O resto da carteira está certo. Tente de novo; se persistir, o servidor do host pode ter caído."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      </Card>
    );
  }

  const hasChart = all.length >= 2;
  const returnValue = Number(portfolio.total_return_value);
  const positive = returnValue >= 0;
  const sign = positive ? "+" : "−";

  return (
    <Card>
      <CardHeader>
        {title}
        <CardAction>
          <div className="flex items-center gap-2">
            {hasChart && (
              <ToggleGroup
                variant="segmented"
                size="xs"
                aria-label="Modo do gráfico"
                value={[mode]}
                onValueChange={(values) => {
                  if (values[0] === "gain" || values[0] === "class") setMode(values[0]);
                }}
              >
                <ToggleGroupItem value="gain">Ganho</ToggleGroupItem>
                <ToggleGroupItem value="class">Por classe</ToggleGroupItem>
              </ToggleGroup>
            )}
            <ToggleGroup
              variant="segmented"
              size="xs"
              aria-label="Período do gráfico"
              value={[period]}
              onValueChange={(values) => {
                const next = PERIODS.find((p) => p.value === values[0]);
                if (next) setPeriod(next.value);
              }}
            >
              {PERIODS.map((p) => (
                <ToggleGroupItem key={p.value} value={p.value} disabled={!isPeriodAvailable(all, p.value)}>
                  {p.label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>
        </CardAction>
      </CardHeader>

      <CardContent>
        <div className="grid gap-3.5">
          {/* Patrimônio de hoje e ganho sobre o aportado */}
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
            <span
              className={`font-mono text-[22px] leading-tight font-semibold ${Number(portfolio.total_networth) < 0 ? "text-destructive" : ""}`}
            >
              {displaySignedMoney(portfolio.total_networth)}
            </span>
            {returnValue !== 0 && (
              <Badge variant={positive ? "success" : "destructive"} numeric>
                {sign}
                {displayMoney(Math.abs(returnValue))} · {sign}
                {displayPercent(Math.abs(Number(portfolio.total_return_pct)), 1)} sobre o aportado
              </Badge>
            )}
          </div>

          {hasChart ? (
            <div ref={attachWidth} className="grid min-w-0 gap-3">
              {width > 0 &&
                (mode === "gain" ? (
                  <>
                    <NetworthGainChart points={points} width={width} />
                    <GainLegend points={points} />
                  </>
                ) : (
                  <NetworthClassPanels points={points} width={width} />
                ))}
            </div>
          ) : (
            <Empty variant="dashed">
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <LineChartIcon />
                </EmptyMedia>
                <EmptyTitle>O gráfico começa no próximo pregão</EmptyTitle>
                <EmptyDescription>Cada dia simulado vira um ponto aqui.</EmptyDescription>
              </EmptyHeader>
            </Empty>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function GainLegend({ points }: { points: NetworthPoint[] }) {
  const hasDebt = points.some((p) => p.debt > 0);
  const hasGoal = points.some((p) => p.goal !== undefined);

  return (
    <ul className="flex flex-wrap items-center gap-x-3.5 gap-y-1 text-xs text-muted-foreground">
      <li className="flex items-center gap-1.5">
        <span className="w-3.5 border-t-2 border-foreground" aria-hidden="true" />
        Patrimônio
      </li>
      <li className="flex items-center gap-1.5">
        <span className="size-2.25 rounded-xs bg-muted ring-1 ring-input ring-inset" aria-hidden="true" />
        Aportado · do seu bolso
      </li>
      <li className="flex items-center gap-1.5">
        <span className="size-2.25 rounded-xs bg-success/30" aria-hidden="true" />
        Ganho
      </li>
      <li className="flex items-center gap-1.5">
        <span className="size-2.25 rounded-xs bg-destructive/30" aria-hidden="true" />
        Perda
      </li>
      {hasDebt && (
        <li className="flex items-center gap-1.5">
          <span className="size-2.25 rounded-xs bg-destructive/20" aria-hidden="true" />
          Dívida · abaixo do zero
        </li>
      )}
      {hasGoal && (
        <li className="flex items-center gap-1.5">
          <span className="w-3.5 border-t-2 border-dotted border-foreground" aria-hidden="true" />
          Meta
        </li>
      )}
    </ul>
  );
}
