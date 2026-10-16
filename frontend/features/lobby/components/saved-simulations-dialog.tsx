import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Play, Search, Trophy, Zap } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/shared/components/ui/dialog";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { cn } from "@/shared/lib/utils";
import { displayDate, displayMonthSlashYear, parseLocalDate } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SimulationListItem } from "@/types";

type StatusFilter = "ALL" | SimulationListItem["status"];

const FILTERS: { value: StatusFilter; label: string }[] = [
  { value: "ALL", label: "Todas" },
  { value: "PAUSED", label: "Pausadas" },
  { value: "FINISHED", label: "Terminadas" },
];

type SavedSimulationsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isHost: boolean;
  selectedSimulationId: number | null;
};

export function SavedSimulationsDialog({
  open,
  onOpenChange,
  isHost,
  selectedSimulationId,
}: SavedSimulationsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[calc(100vh-4rem)] overflow-y-auto sm:max-w-[640px]">
        <SavedSimulationsContent
          isHost={isHost}
          selectedSimulationId={selectedSimulationId}
          onSelected={() => onOpenChange(false)}
        />
      </DialogContent>
    </Dialog>
  );
}

// O conteúdo desmonta quando o diálogo fecha: cada abertura nasce com busca e
// filtro limpos e busca a lista de novo, trazendo as partidas recém-salvas.
function SavedSimulationsContent({
  isHost,
  selectedSimulationId,
  onSelected,
}: {
  isHost: boolean;
  selectedSimulationId: number | null;
  onSelected: () => void;
}) {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<StatusFilter>("ALL");

  const { data, isLoading, error, refetch } = useApiQuery({ ...simulationListOptions(), refetchOnMount: "always" });

  const {
    mutate: selectSimulation,
    isPending: loading,
    variables,
  } = useApiMutation({
    mutationFn: (id: number) => apiFetch<void>("/api/simulation/selection", { method: "PUT", body: { id } }),
    onSuccess: onSelected,
    onError: (err) => toastApiError(err),
  });

  const term = search.trim().toLowerCase();
  // A lista vem da mais recente para a mais antiga: a primeira é a que o atalho do lobby seleciona
  const lastSimulation = data?.[0];
  const items = (data ?? []).filter(
    (s) => (filter === "ALL" || s.status === filter) && (!term || s.name.toLowerCase().includes(term)),
  );

  const renderList = () => {
    if (isLoading) {
      return Array.from({ length: 4 }, (_, i) => (
        <div key={i} className="grid gap-2 border-b border-muted px-6 py-3.5">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-3 w-64" />
        </div>
      ));
    }
    if (error) {
      return (
        <ErrorState
          title="Não deu pra carregar as simulações"
          description="Confira se o servidor do host está ligado."
          error={error}
          onRetry={() => void refetch()}
        />
      );
    }
    if (items.length === 0) {
      return (
        <p className="px-6 py-12 text-center text-muted-foreground">
          {data?.length
            ? "Nenhuma simulação com esse filtro."
            : "Nenhuma partida salva ainda. Quando uma partida for pausada ou terminar, ela aparece aqui."}
        </p>
      );
    }
    return items.map((s) => {
      // A primeira da lista inteira, se pausada, é a que o atalho "Selecionar a última simulação" escolhe
      const resumedByLobby = isHost && s.id === lastSimulation?.id && s.status === "PAUSED";
      const selected = s.id === selectedSimulationId;
      return (
      <div
        key={s.id}
        className={cn(
          "flex items-center gap-4 border-b border-muted px-6 py-3.5 last:border-0",
          resumedByLobby && "bg-info-soft shadow-[inset_3px_0_0_var(--primary)]",
        )}
      >
        <div className="grid min-w-0 flex-1 gap-1">
          <div className="flex items-center gap-2">
            <span className="truncate font-semibold">{s.name}</span>
            {s.status === "FINISHED" ? (
              <Badge variant="success" size="sm">
                Terminou{s.winner_nickname && ` · ${s.winner_nickname} venceu`}
              </Badge>
            ) : (
              <Badge variant="info" size="sm">
                {s.resume_from ? `Pausada em ${displayDate(parseLocalDate(s.resume_from))}` : "Não começou"}
              </Badge>
            )}
          </div>
          <span className="font-mono text-xs text-muted-foreground">
            {displayMonthSlashYear(s.start_date)} → {displayMonthSlashYear(s.end_date)}
          </span>
          <span className="text-xs text-muted-foreground">
            {s.players_count <= 1 ? "Solo" : `${s.players_count} jogadores`} ·{" "}
            {VICTORY_CRITERIA[s.victory_criterion].label}
          </span>
          {resumedByLobby && (
            <span className="flex items-center gap-1 text-xs font-semibold text-primary">
              <Zap className="size-3" />É esta que o “Selecionar a última simulação” do lobby escolhe
            </span>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate(`/match-result/${s.id}`)}>
          <Trophy />
          Resultado
        </Button>
        {isHost && s.status === "PAUSED" && (
          <Button size="sm" disabled={loading || selected} onClick={() => selectSimulation(s.id)}>
            <Play />
            {selected ? "Selecionada" : loading && variables === s.id ? "Selecionando…" : "Selecionar"}
          </Button>
        )}
      </div>
      );
    });
  };

  return (
    <>
      <DialogHeader variant="divided">
        <DialogTitle>Simulações salvas</DialogTitle>
        <DialogDescription>
          {isHost
            ? "Selecione uma partida para continuar de onde parou ou veja quem venceu."
            : "Só o host continua uma partida; você pode ver os resultados."}
        </DialogDescription>
      </DialogHeader>

      <div className="flex flex-wrap items-center gap-3">
        <InputGroup className="flex-1">
          <InputGroupAddon>
            <Search />
          </InputGroupAddon>
          <InputGroupInput value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por nome" />
        </InputGroup>
        <ToggleGroup
          variant="segmented"
          aria-label="Filtrar por situação"
          value={[filter]}
          onValueChange={(values) => values[0] && setFilter(values[0] as StatusFilter)}
        >
          {FILTERS.map((f) => (
            <ToggleGroupItem key={f.value} value={f.value}>
              {f.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      {/* Listagem sem altura fixa: quem rola é o diálogo */}
      <div className="-mx-6 -mb-6 overflow-hidden rounded-b-xl border-t border-border">{renderList()}</div>
    </>
  );
}
