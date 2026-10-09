import { useState } from "react";
import { Search } from "lucide-react";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Input } from "@/shared/components/ui/input";
import { ScrollArea } from "@/shared/components/ui/scroll-area";
import { Spinner } from "@/shared/components/ui/spinner";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { displayDate } from "@/shared/lib/utils/display";

interface SimulationPickerProps {
  selected: number[];
  onToggle: (id: number) => void;
}

export function SimulationPicker({ selected, onToggle }: SimulationPickerProps) {
  const [search, setSearch] = useState("");
  const { data, isLoading: loading, error } = useApiQuery(simulationListOptions());

  const term = search.trim().toLowerCase();
  const items = (data ?? []).filter((s) => s.name.toLowerCase().includes(term));

  const renderList = () => {
    if (loading) {
      return (
        <div className="flex h-40 items-center justify-center">
          <Spinner className="size-6" />
        </div>
      );
    }

    if (error) {
      return <p className="px-4 py-6 text-center text-sm text-muted-foreground">Erro ao carregar simulações.</p>;
    }

    if (items.length === 0) {
      return <p className="px-4 py-6 text-center text-sm text-muted-foreground">Nenhuma simulação encontrada.</p>;
    }

    return (
      <ul className="divide-y">
        {items.map((s) => (
          <li key={s.id}>
            <label className="flex cursor-pointer items-start gap-3 px-4 py-3 transition-colors hover:bg-accent">
              <Checkbox className="mt-0.5" checked={selected.includes(s.id)} onCheckedChange={() => onToggle(s.id)} />
              <div className="min-w-0">
                <p className="truncate font-medium">{s.name}</p>
                <p className="text-xs text-muted-foreground">
                  {displayDate(`${s.start_date}T00:00:00`)} a {displayDate(`${s.end_date}T00:00:00`)}
                </p>
              </div>
            </label>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <aside className="flex w-full flex-col gap-3 border-b p-4 md:w-72 md:border-r md:border-b-0">
      <h2 className="text-lg font-semibold">Simulações</h2>

      {/* Busca */}
      <div className="relative">
        <Search className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por nome..." className="pl-9" />
      </div>

      {/* Lista */}
      <ScrollArea className="h-72 rounded-md border md:h-auto md:flex-1">{renderList()}</ScrollArea>
    </aside>
  );
}
