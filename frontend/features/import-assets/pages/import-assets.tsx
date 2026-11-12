import { useState } from "react";
import { CalendarDays } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { ErrorState } from "@/shared/components/error-state";
import { useSeriesCoverage } from "@/shared/hooks/queries/useSeriesCoverage";
import { useDownloadIndicators } from "../hooks/mutations/useDownloadIndicators";
import { useGeneratedFuture } from "../hooks/queries/useGeneratedFuture";
import { ADD_ASSET_INPUT_ID, AddAssetPanel } from "../components/add-asset-panel";
import { AssetsTable } from "../components/assets-table";
import { CoverageSummary } from "../components/coverage-summary";
import { GenerateFutureButton } from "../components/generate-future-button";
import { GenerateFutureDialog } from "../components/generate-future-dialog";
import { HowToRead } from "../components/how-to-read";
import { IndicatorsTable } from "../components/indicators-table";
import { needsAttention } from "../lib/attention";
import { timelineRange } from "../lib/timeline";

type Tab = "indicators" | "assets";

const SKELETON_ROWS = 6;

export default function ImportAssetsPage() {
  const { data: series, isLoading, error, refetch } = useSeriesCoverage();
  const [tab, setTab] = useState<Tab>("indicators");
  // Ação com a classificação aberta na própria linha da tabela
  const [classifying, setClassifying] = useState<string | null>(null);
  // Diálogo de geração: nulo fechado; `redrawSeed` abre com uma semente nova
  const [generating, setGenerating] = useState<{ redrawSeed: boolean } | null>(null);

  const { data: future } = useGeneratedFuture();

  const downloadIndicators = useDownloadIndicators();

  const all = series ?? [];
  const hasData = all.some((s) => s.start);
  const stocks = all.filter((s) => s.kind === "STOCK");
  const indicators = all.filter((s) => s.kind !== "STOCK");
  const attention = all.filter(needsAttention).length;
  // As duas abas dividem o mesmo eixo: a barra de um indicador e a de um ativo se comparam
  const range = timelineRange(all);

  const renderSeries = () => {
    if (isLoading) {
      return (
        <Card>
          <CardContent>
            <div className="grid gap-5">
              {Array.from({ length: SKELETON_ROWS }, (_, i) => (
                <div
                  key={i}
                  className="grid grid-cols-[minmax(0,1fr)_176px_minmax(0,1.4fr)_144px_96px] items-center gap-4"
                >
                  <div className="grid gap-1.5">
                    <Skeleton className="h-4 w-2/3" />
                    <Skeleton className="h-3 w-1/3" />
                  </div>
                  <Skeleton className="h-4" />
                  <Skeleton className="h-2.5" />
                  <Skeleton className="h-5 w-20" />
                  <Skeleton className="ml-auto h-8 w-20" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      );
    }
    if (error) {
      return (
        <Card>
          <CardContent>
            <ErrorState
              title="Não deu pra carregar as séries"
              description="O servidor não respondeu. A base continua como estava."
              error={error}
              onRetry={() => void refetch()}
            />
          </CardContent>
        </Card>
      );
    }
    if (!hasData) {
      return (
        <Card>
          <CardContent>
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <CalendarDays />
                </EmptyMedia>
                <EmptyTitle>A base está vazia</EmptyTitle>
                <EmptyDescription>
                  Baixe os indicadores (juros, inflação, Ibovespa e as expectativas do Focus) e adicione pelo menos um
                  ativo. Sem CDI, SELIC, IPCA e Ibovespa na data inicial, a partida não começa.
                </EmptyDescription>
              </EmptyHeader>
              <EmptyContent className="flex-row justify-center">
                <Button disabled={downloadIndicators.isPending} onClick={() => downloadIndicators.mutate()}>
                  {downloadIndicators.isPending && <Spinner />}
                  Baixar indicadores
                </Button>
                <Button variant="outline" onClick={() => document.getElementById(ADD_ASSET_INPUT_ID)?.focus()}>
                  Adicionar ativo
                </Button>
              </EmptyContent>
            </Empty>
          </CardContent>
        </Card>
      );
    }
    return null;
  };

  const placeholder = renderSeries();

  return (
    <section className="flex flex-col gap-5">
      {/* Cabeçalho */}
      <header className="flex items-end justify-between gap-4">
        <div className="grid gap-1">
          <h1 className="text-2xl font-bold">Central de dados</h1>
          <p className="text-muted-foreground">
            Os preços e indicadores que as partidas usam. Só dá pra mexer fora da partida.
          </p>
        </div>
        <GenerateFutureButton onClick={() => setGenerating({ redrawSeed: true })} />
      </header>

      {hasData && !isLoading && (
        <CoverageSummary series={all} future={future} onGenerate={() => setGenerating({ redrawSeed: false })} />
      )}

      {placeholder ? (
        // Carregando, com erro ou sem dados: o painel de adicionar ativo fica à mostra
        <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
          {placeholder}
          <aside className="grid gap-5">
            <AddAssetPanel onClassify={setClassifying} />
            <HowToRead />
          </aside>
        </div>
      ) : (
        <Tabs value={tab} onValueChange={(value) => setTab(value as Tab)}>
          <TabsList variant="line">
            <TabsTrigger value="indicators">
              Indicadores e expectativas
              <Badge variant="secondary" size="sm" aria-label={`${indicators.length} séries`}>
                {indicators.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="assets">
              Ativos
              <Badge variant="secondary" size="sm" aria-label={`${stocks.length} ativos`}>
                {stocks.length}
              </Badge>
              {attention > 0 && (
                <Badge variant="warning" size="sm">
                  {attention} {attention === 1 ? "pede atenção" : "pedem atenção"}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Indicadores, economia do país e Focus, em largura inteira */}
          <TabsContent value="indicators">
            <div className="pt-3">
              <IndicatorsTable series={indicators} range={range} />
            </div>
          </TabsContent>

          {/* Ativos importados, com o painel de adicionar e a legenda ao lado */}
          <TabsContent value="assets">
            <div className="grid items-start gap-5 pt-3 xl:grid-cols-[minmax(0,1fr)_320px]">
              <AssetsTable series={stocks} range={range} classifying={classifying} onClassify={setClassifying} />
              <aside className="grid gap-5">
                <AddAssetPanel onClassify={setClassifying} />
                <HowToRead />
              </aside>
            </div>
          </TabsContent>
        </Tabs>
      )}

      <GenerateFutureDialog
        open={generating !== null}
        redrawSeed={generating?.redrawSeed ?? false}
        onOpenChange={(open) => !open && setGenerating(null)}
      />
    </section>
  );
}
