import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { FlaskConical, RotateCcw, Search, Trophy, Zap } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/shared/components/ui/dialog";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import { cn } from "@/shared/lib/utils";
import { displayDate, displayMonthSlashYear, parseLocalDate } from "@/shared/lib/utils/display";
import { winRuleLabel } from "@/shared/lib/game-types";
import type { SimulationListItem } from "@/types";
import { useClearSimulationSelection } from "../hooks/mutations/useClearSimulationSelection";
import { useSelectSimulation } from "../hooks/mutations/useSelectSimulation";
import { DeleteSimulationButton } from "./delete-simulation-button";
import { RoomOverflowAlert } from "./room-overflow-alert";

type StatusFilter = "ALL" | SimulationListItem["status"];

type SavedKind = "matches" | "backtests";

/** Concluído, o backtest tem vencedora; parado, só quem está na frente até onde rodou. */
function backtestLeaderText(s: SimulationListItem) {
  if (s.winner_nickname) return ` · venceu ${s.winner_nickname}`;
  return s.leader_nickname ? ` · na frente: ${s.leader_nickname}` : "";
}

const FILTERS: Record<SavedKind, { value: StatusFilter; label: string }[]> = {
  matches: [
    { value: "ALL", label: "Todas" },
    { value: "PAUSED", label: "Pausadas" },
    { value: "FINISHED", label: "Terminadas" },
  ],
  backtests: [
    { value: "ALL", label: "Todos" },
    { value: "PAUSED", label: "Parados" },
    { value: "FINISHED", label: "Concluídos" },
  ],
};

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
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<StatusFilter>("ALL");
  const [kind, setKind] = useState<SavedKind>("matches");

  const { data, isLoading, error, refetch } = useSimulationList({ refetchOnMount: "always" });

  const {
    mutate: selectSimulation,
    isPending: loading,
    variables,
  } = useSelectSimulation();

  const { mutate: clearSelection, isPending: clearing } = useClearSimulationSelection();

  // Sem salva selecionada o lobby já é de nova partida: "Começar" só fecha o diálogo
  const startNew = () =>
    selectedSimulationId === null ? onSelected() : clearSelection(undefined, { onSuccess: onSelected });

  // Quem entra ou sai da sala muda quais partidas ainda cabem; uma partida excluída sai da lista
  const refreshFit = () => void queryClient.invalidateQueries({ queryKey: queryKeys.simulationList() });
  useRealtime("player_join", refreshFit);
  useRealtime("player_exit", refreshFit);
  useRealtime("simulation_deleted", refreshFit);

  const term = search.trim().toLowerCase();
  const matches = (data ?? []).filter((s) => !s.is_backtest);
  const backtests = (data ?? []).filter((s) => s.is_backtest);
  const inKind = kind === "matches" ? matches : backtests;
  // A lista vem da mais recente para a mais antiga: a primeira partida é a que o atalho do lobby seleciona
  const lastSimulation = matches[0];
  const empty = !isLoading && !error && data?.length === 0;
  // Com o que escolher (ou ainda carregando) o host também começa uma partida nova daqui
  const choosing = isHost && !empty;
  const items = inKind.filter(
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
          {inKind.length
            ? "Nenhuma simulação com esse filtro."
            : kind === "backtests"
              ? "Nenhum backtest salvo ainda. Quando um backtest terminar ou for parado, ele aparece aqui."
              : "Nenhuma partida salva ainda. Quando uma partida for pausada ou terminar, ela aparece aqui."}
        </p>
      );
    }
    return items.map((s) => {
      // A lista vem da jogada mais recente para a mais antiga: a primeira, se pausada, é a última partida salva
      const isLast = s.id === lastSimulation?.id && s.status === "PAUSED";
      const selected = s.id === selectedSimulationId;
      return (
      <div
        key={s.id}
        className={cn(
          "flex items-center gap-4 border-b border-muted px-6 py-3.5 last:border-0",
          selected && "bg-info-soft shadow-[inset_3px_0_0_var(--primary)]",
        )}
      >
        <div className="grid min-w-0 flex-1 gap-1">
          <div className="flex items-center gap-2">
            <span className="truncate font-semibold">{s.name}</span>
            {s.status === "FINISHED" ? (
              <Badge variant="success" size="sm">
                {s.is_backtest ? "Concluído" : `Terminou${s.winner_nickname ? ` · ${s.winner_nickname} venceu` : ""}`}
              </Badge>
            ) : (
              <Badge variant="info" size="sm">
                {s.resume_from
                  ? `${s.is_backtest ? "Parado" : "Pausada"} em ${displayDate(parseLocalDate(s.resume_from))}`
                  : "Não começou"}
              </Badge>
            )}
          </div>
          <span className="font-mono text-xs text-muted-foreground">
            {displayMonthSlashYear(s.start_date)} → {displayMonthSlashYear(s.end_date)}
          </span>
          <span className="text-xs text-muted-foreground">
            {s.is_backtest
              ? `${s.players_count} ${s.players_count === 1 ? "estratégia" : "estratégias"}${backtestLeaderText(s)}`
              : `${s.players_count <= 1 ? "Solo" : `${s.players_count} jogadores`} · ${winRuleLabel(s.game_type, s.victory_criterion)}`}
          </span>
          {isHost && !s.is_backtest && s.status === "PAUSED" && s.room_overflow.length > 0 && (
            <RoomOverflowAlert names={s.room_overflow} />
          )}
          {isLast && (
            <span className="flex items-center gap-1 text-xs font-semibold text-primary">
              <Zap className="size-3" />Última partida salva
            </span>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={() => void navigate(`/match-result/${s.id}`)}>
          <Trophy />
          Resultado
        </Button>
        {isHost && s.is_backtest && (
          <Button variant="outline" size="sm" onClick={() => void navigate(`/backtest/new?from=${s.id}`)}>
            <RotateCcw />
            Rodar de novo
          </Button>
        )}
        {isHost && !s.is_backtest && s.status === "PAUSED" && (
          <Button
            size="sm"
            variant={s.room_overflow.length > 0 ? "secondary" : "default"}
            disabled={loading || selected || s.room_overflow.length > 0}
            onClick={() => selectSimulation(s.id, { onSuccess: onSelected })}
          >
            {selected
              ? "Selecionada"
              : s.room_overflow.length > 0
                ? "Indisponível"
                : loading && variables === s.id
                  ? "Selecionando…"
                  : "Selecionar"}
          </Button>
        )}
        {isHost && <DeleteSimulationButton simulation={s} disabled={selected} />}
      </div>
      );
    });
  };

  return (
    <>
      <DialogHeader variant="divided">
        <DialogTitle>{choosing ? "Escolher partida" : "Simulações salvas"}</DialogTitle>
        <DialogDescription>
          {!isHost
            ? "Só o host continua uma partida; você pode ver os resultados."
            : empty
              ? "Aqui você continua partidas antigas e vê quem venceu."
              : "Comece uma nova partida ou continue uma salva de onde parou."}
        </DialogDescription>
      </DialogHeader>

      {/* Partidas e backtests */}
      <div className="-mx-6 -mt-4 px-6">
        <Tabs
          value={kind}
          onValueChange={(value) => {
            setKind(value as SavedKind);
            setFilter("ALL");
          }}
        >
          <TabsList variant="line">
            <TabsTrigger value="matches">
              Partidas
              <Badge variant="secondary" size="tag">
                {matches.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="backtests">
              Backtests
              <Badge variant="secondary" size="tag">
                {backtests.length}
              </Badge>
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Novo backtest: ação do host, em faixa própria acima da lista */}
      {isHost && kind === "backtests" && !isLoading && !error && (
        <div className="-mx-6 -mt-4 flex items-center gap-3 border-b border-info-border bg-info-soft px-6 py-4">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-[9px] bg-primary text-primary-foreground">
            <FlaskConical className="size-[18px]" />
          </span>
          <div className="grid min-w-0 flex-1">
            <span className="font-bold">Novo backtest</span>
            <span className="text-xs text-muted-foreground">Estratégias contra o mercado, sem esperar o jogo</span>
          </div>
          <Button size="sm" onClick={() => void navigate("/backtest/new")}>
            Configurar
          </Button>
        </div>
      )}

      {/* Nova partida: ação do host, em faixa própria acima da lista de salvas */}
      {choosing && kind === "matches" && (
        <div className="-mx-6 -mt-4 flex items-center gap-3 border-b border-info-border bg-info-soft px-6 py-4">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-[9px] bg-primary text-primary-foreground">
            <Zap className="size-[18px]" />
          </span>
          <div className="grid min-w-0 flex-1">
            <span className="font-bold">Nova partida</span>
            <span className="text-xs text-muted-foreground">Do zero, com as regras do lobby</span>
          </div>
          <Button size="sm" disabled={clearing || loading} onClick={startNew}>
            Começar
          </Button>
        </div>
      )}

      {choosing && kind === "matches" && (
        <span className="-mb-2 text-[11px] font-semibold tracking-[0.06em] text-faint-foreground uppercase">
          Partidas salvas
        </span>
      )}

      {/* Sem partida salva não há o que buscar nem filtrar */}
      {!empty && (
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
            {FILTERS[kind].map((f) => (
              <ToggleGroupItem key={f.value} value={f.value}>
                {f.label}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </div>
      )}

      {/* Listagem sem altura fixa: quem rola é o diálogo */}
      <div className="-mx-6 -mb-6 overflow-hidden rounded-b-xl border-t border-border">{renderList()}</div>
    </>
  );
}
