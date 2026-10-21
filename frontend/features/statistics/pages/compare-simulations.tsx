import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { GitCompareArrows } from "lucide-react";
import { useSearchParams } from "react-router-dom";
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
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useAuth } from "@/shared/hooks/useAuth";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { SimulationPicker } from "../components/compare/simulation-picker";
import { SimulationSummaries } from "../components/compare/simulation-summaries";
import { StatisticsReport } from "../components/statistics-report";

type Show = "ALL" | "YOU";

/** `?ids=3,5` abre a comparação com essas partidas já escolhidas, na ordem dada. */
function idsFromQuery(params: URLSearchParams) {
  return (params.get("ids") ?? "")
    .split(",")
    .map(Number)
    .filter((id) => Number.isInteger(id) && id > 0);
}

export default function CompareSimulationsPage() {
  const [params] = useSearchParams();
  const [selected, setSelected] = useState<number[]>(() => idsFromQuery(params));
  const [show, setShow] = useState<Show>("ALL");
  const { user } = useAuth();
  const { data: simulations } = useQuery(simulationListOptions());

  // A ordem de escolha define a letra: quem entra depois fica com a próxima
  const toggle = (id: number) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  const latestTwo = [...(simulations ?? [])].sort((a, b) => b.id - a.id).slice(0, 2);

  return (
    <div className="grid gap-5">
      {/* Cabeçalho */}
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="grid gap-1">
          <h1 className="text-2xl font-bold">Comparar simulações</h1>
          <p className="text-muted-foreground">Veja lado a lado como cada um se saiu em partidas diferentes.</p>
        </div>
        <div className="flex items-center gap-2.5">
          <span className="text-xs font-medium text-muted-foreground">Mostrar</span>
          <ToggleGroup
            variant="segmented"
            aria-label="Jogadores mostrados"
            value={[show]}
            onValueChange={(values) => values[0] && setShow(values[0] as Show)}
          >
            <ToggleGroupItem value="ALL">Todos os jogadores</ToggleGroupItem>
            <ToggleGroupItem value="YOU" disabled={!user}>
              Só você
            </ToggleGroupItem>
          </ToggleGroup>
        </div>
      </header>

      <div className="grid items-start gap-5 lg:grid-cols-[300px_minmax(0,1fr)]">
        <SimulationPicker selected={selected} onToggle={toggle} />

        <div className="grid min-w-0 gap-5">
          {selected.length === 0 ? (
            <Card>
              <CardContent>
                <Empty>
                  <EmptyHeader>
                    <EmptyMedia variant="icon">
                      <GitCompareArrows />
                    </EmptyMedia>
                    <EmptyTitle>Escolha duas ou mais partidas</EmptyTitle>
                    <EmptyDescription>
                      Cada uma ganha uma letra e uma cor. Uma boa primeira comparação: suas duas partidas mais recentes.
                    </EmptyDescription>
                  </EmptyHeader>
                  {latestTwo.length === 2 && (
                    <EmptyContent>
                      <Button onClick={() => setSelected(latestTwo.map((s) => s.id))}>
                        Comparar as 2 mais recentes
                      </Button>
                    </EmptyContent>
                  )}
                </Empty>
              </CardContent>
            </Card>
          ) : (
            <>
              <SimulationSummaries simulationIds={selected} currentPlayerName={user?.nickname} />
              <StatisticsReport
                simulationIds={selected}
                currentPlayerName={user?.nickname}
                onlyPlayer={show === "YOU" ? user?.nickname : undefined}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
