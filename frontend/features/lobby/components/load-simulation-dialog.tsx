import { useEffect, useMemo, useState } from "react";
import { Search, Play } from "lucide-react";
import { toast } from "sonner";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import { ScrollArea } from "@/shared/components/ui/scroll-area";
import { Spinner } from "@/shared/components/ui/spinner";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayDate, displayMoneyCompact } from "@/shared/lib/utils/display";
import { cn } from "@/shared/lib/utils";
import type { SimulationInfo, SimulationListItem } from "@/types";

interface LoadSimulationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isHost: boolean;
}

export function LoadSimulationDialog({ open, onOpenChange, isHost }: LoadSimulationDialogProps) {
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data, isLoading: loading, error, refetch } = useApiQuery({
    queryKey: queryKeys.simulationList(),
    queryFn: ({ signal }) => apiFetch<SimulationListItem[]>("/api/simulation/list", { signal }),
    enabled: false,
  });

  // Recarrega a lista (e reseta a seleção/busca) sempre que o dialog abre,
  // garantindo que simulações recém-criadas apareçam.
  useEffect(() => {
    if (open) {
      setSearch("");
      setSelectedId(null);
      void refetch();
    }
  }, [open, refetch]);

  const { mutate: loadSimulation, isPending: loadingLoad } = useApiMutation({
    mutationFn: (body: { id: number }) => apiFetch<SimulationInfo>("/api/simulation/load", { method: "POST", body }),
    onSuccess: () => onOpenChange(false),
    onError: (err) => toast.error(err.message),
  });

  const items = useMemo(() => {
    const term = search.trim().toLowerCase();
    const list = data ?? [];
    if (!term) return list;
    return list.filter((s) => s.name.toLowerCase().includes(term));
  }, [data, search]);

  const renderList = () => {
    if (loading) {
      return (
        <div className="flex h-72 items-center justify-center">
          <Spinner className="size-6" />
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex h-72 items-center justify-center px-4 text-center text-sm text-muted-foreground">
          Erro ao carregar simulações.
        </div>
      );
    }

    if (items.length === 0) {
      return (
        <div className="flex h-72 items-center justify-center px-4 text-center text-sm text-muted-foreground">
          Nenhuma simulação encontrada.
        </div>
      );
    }

    return (
      <ul className="divide-y">
        {items.map((s) => {
          const selected = s.id === selectedId;
          return (
            <li key={s.id}>
              <button
                type="button"
                onClick={() => setSelectedId(s.id)}
                aria-pressed={selected}
                className={cn(
                  "w-full px-4 py-3 text-left transition-colors hover:bg-accent",
                  selected && "bg-accent"
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="font-medium">{s.name}</p>
                  <span className="text-xs text-muted-foreground">{displayMoneyCompact(s.starting_cash)}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Criada em {displayDate(s.created_at)} · Simulada em {displayDate(s.last_simulated_at)}
                </p>
              </button>
            </li>
          );
        })}
      </ul>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[80vh] flex-col sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Carregar Simulação</DialogTitle>
          <DialogDescription>
            Selecione uma simulação salva para continuar de onde parou.
          </DialogDescription>
        </DialogHeader>

        {/* Barra de pesquisa (altura fixa) */}
        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nome..."
            className="pl-9"
          />
        </div>

        {/* Lista (altura fixa e scrollável — não encolhe ao filtrar) */}
        <ScrollArea className="h-72 rounded-md border">{renderList()}</ScrollArea>

        <DialogFooter>
          <Button
            type="button"
            variant="success"
            className="w-full sm:w-auto"
            disabled={selectedId === null || !isHost || loadingLoad}
            onClick={() => selectedId !== null && loadSimulation({ id: selectedId })}
          >
            <Play fill="currentColor" />
            Carregar e Iniciar Simulação
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
