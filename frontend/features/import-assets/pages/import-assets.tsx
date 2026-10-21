import { useState } from "react";
import { CalendarDays } from "lucide-react";
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
import { ErrorState } from "@/shared/components/error-state";
import { useSeriesCoverage } from "@/shared/hooks/queries/useSeriesCoverage";
import { useDownloadIndicators } from "../hooks/mutations/useDownloadIndicators";
import { useGeneratedFuture } from "../hooks/queries/useGeneratedFuture";
import { ADD_ASSET_INPUT_ID, AddAssetPanel } from "../components/add-asset-panel";
import { CoverageSummary } from "../components/coverage-summary";
import { GenerateFutureButton } from "../components/generate-future-button";
import { GenerateFutureDialog } from "../components/generate-future-dialog";
import { HowToRead } from "../components/how-to-read";
import { SeriesTable } from "../components/series-table";

export default function ImportAssetsPage() {
  const { data: series, isLoading, error, refetch } = useSeriesCoverage();
  // Ação com a classificação aberta na própria linha da tabela
  const [classifying, setClassifying] = useState<string | null>(null);
  // Diálogo de geração: nulo fechado; `redrawSeed` abre com uma semente nova
  const [generating, setGenerating] = useState<{ redrawSeed: boolean } | null>(null);

  const { data: future } = useGeneratedFuture();

  const downloadIndicators = useDownloadIndicators();

  const hasData = (series ?? []).some((s) => s.start);

  const renderSeries = () => {
    if (isLoading) {
      return (
        <Card>
          <CardContent>
            <div className="grid gap-4">
              {Array.from({ length: 5 }, (_, i) => (
                <div key={i} className="grid grid-cols-[120px_200px_1fr_90px] gap-4">
                  <Skeleton className="h-4" />
                  <Skeleton className="h-4" />
                  <Skeleton className="h-4" />
                  <Skeleton className="h-4" />
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
              description="Confira se o servidor do host está ligado."
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
                  Comece pelos indicadores: sem CDI, SELIC, IPCA e Ibovespa na data inicial, a partida não começa.
                  Depois adicione as ações que quer negociar.
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
    return <SeriesTable series={series ?? []} classifying={classifying} onClassify={setClassifying} />;
  };

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

      {hasData && (
        <CoverageSummary
          series={series ?? []}
          future={future}
          onGenerate={() => setGenerating({ redrawSeed: false })}
        />
      )}

      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        {renderSeries()}
        <aside className="grid gap-5">
          <AddAssetPanel onClassify={setClassifying} />
          <HowToRead />
        </aside>
      </div>

      <GenerateFutureDialog
        open={generating !== null}
        redrawSeed={generating?.redrawSeed ?? false}
        onOpenChange={(open) => !open && setGenerating(null)}
      />
    </section>
  );
}
