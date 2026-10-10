import { useState } from "react";
import { Search } from "lucide-react";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Input } from "@/shared/components/ui/input";
import { ScrollArea } from "@/shared/components/ui/scroll-area";

// Limite da rota: a grade fica legível até 20 ativos
export const MAX_TICKERS = 20;

interface TickerPickerProps {
  tickers: string[];
  selected: string[];
  onToggle: (ticker: string) => void;
}

export function TickerPicker({ tickers, selected, onToggle }: TickerPickerProps) {
  const [search, setSearch] = useState("");

  const term = search.trim().toUpperCase();
  const items = tickers.filter((t) => t.includes(term));
  const full = selected.length >= MAX_TICKERS;

  return (
    <aside className="flex w-full flex-col gap-3 border-b p-4 md:w-60 md:border-r md:border-b-0">
      <div>
        <h2 className="text-lg font-semibold">Ativos</h2>
        <p className="text-xs text-muted-foreground">
          {selected.length} de até {MAX_TICKERS} selecionados
        </p>
      </div>

      {/* Busca */}
      <div className="relative">
        <Search className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar ticker..." className="pl-9" />
      </div>

      {/* Lista */}
      <ScrollArea className="h-72 rounded-md border md:h-auto md:flex-1">
        {items.length === 0 ? (
          <p className="px-4 py-6 text-center text-sm text-muted-foreground">Nenhum ativo encontrado.</p>
        ) : (
          <ul className="divide-y">
            {items.map((ticker) => {
              const checked = selected.includes(ticker);
              return (
                <li key={ticker}>
                  <label className="flex cursor-pointer items-center gap-3 px-4 py-2 transition-colors hover:bg-accent">
                    <Checkbox checked={checked} disabled={!checked && full} onCheckedChange={() => onToggle(ticker)} />
                    <span className="font-medium">{ticker}</span>
                  </label>
                </li>
              );
            })}
          </ul>
        )}
      </ScrollArea>
    </aside>
  );
}
