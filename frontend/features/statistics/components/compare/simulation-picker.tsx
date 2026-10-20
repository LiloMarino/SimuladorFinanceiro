import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorState } from "@/shared/components/error-state";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { cn } from "@/shared/lib/utils";
import { displayMonthSlashYear } from "@/shared/lib/utils/display";
import { winRuleLabel } from "@/shared/lib/game-types";
import type { SimulationListItem } from "@/types";
import { simulationColor, simulationLetter } from "../../lib/player-label";
import { SimulationLetter } from "./simulation-letter";

interface SimulationPickerProps {
  selected: number[];
  onToggle: (id: number) => void;
}

/** "4 jogadores · você em 2º · Nota geral": o resumo de uma linha da lista. */
function describe(s: SimulationListItem) {
  const players = s.players_count === 1 ? "Solo" : `${s.players_count} jogadores`;
  const position = s.my_position !== null && s.players_count > 1 ? ` · você em ${s.my_position}º` : "";
  return `${players}${position} · ${winRuleLabel(s.game_type, s.victory_criterion)}`;
}

/** A lista de simulações salvas: cada uma escolhida ganha a letra e a cor da ordem em que entrou. */
export function SimulationPicker({ selected, onToggle }: SimulationPickerProps) {
  const [search, setSearch] = useState("");
  const { data, isLoading, error, refetch } = useApiQuery(simulationListOptions());

  const term = search.trim().toLowerCase();
  const items = (data ?? []).filter((s) => s.name.toLowerCase().includes(term));

  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>Simulações salvas</CardTitle>
        {data && (
          <CardDescription>
            {selected.length} de {data.length}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid gap-3">
          <InputGroup>
            <InputGroupAddon>
              <Search />
            </InputGroupAddon>
            <InputGroupInput value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por nome" />
          </InputGroup>

          {/* Lista */}
          {isLoading ? (
            <div className="grid gap-2">
              {Array.from({ length: 4 }, (_, i) => (
                <Skeleton key={i} className="h-[66px]" />
              ))}
            </div>
          ) : error ? (
            <ErrorState
              title="Não deu pra carregar as simulações"
              description="Confira se o servidor do host está ligado."
              error={error}
              onRetry={() => void refetch()}
            />
          ) : data?.length === 0 ? (
            <p className="py-4 text-center text-[13px] text-muted-foreground">
              Nenhuma partida salva ainda. Elas aparecem aqui quando terminam ou são salvas no lobby.
            </p>
          ) : items.length === 0 ? (
            <p className="py-4 text-center text-[13px] text-muted-foreground">
              Nenhuma simulação com “{search.trim()}”.{" "}
              <Button variant="link" size="sm" onClick={() => setSearch("")}>
                Limpar busca
              </Button>
            </p>
          ) : (
            <div className="grid gap-2">
              {items.map((s) => {
                const chosen = selected.includes(s.id);
                return (
                  <button
                    key={s.id}
                    type="button"
                    aria-pressed={chosen}
                    onClick={() => onToggle(s.id)}
                    className={cn(
                      "flex w-full items-start gap-3 rounded-[10px] border p-3 text-left transition-colors",
                      chosen ? "border-primary bg-info-soft/50" : "border-border hover:bg-subtle",
                    )}
                  >
                    <SimulationLetter
                      letter={chosen ? simulationLetter(selected, s.id) : null}
                      color={simulationColor(selected, s.id)}
                    />
                    <span className="grid min-w-0 gap-0.5">
                      <span className="truncate font-semibold">{s.name}</span>
                      <span className="font-mono text-xs text-muted-foreground">
                        {displayMonthSlashYear(s.start_date)} → {displayMonthSlashYear(s.resume_from ?? s.end_date)}
                      </span>
                      <span className="text-xs text-muted-foreground">{describe(s)}</span>
                    </span>
                  </button>
                );
              })}
            </div>
          )}

          <p className="text-xs text-faint-foreground">
            Cada simulação escolhida ganha uma letra e uma cor, usadas no ranking e nos gráficos.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
