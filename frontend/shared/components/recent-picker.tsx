import { ChevronDown } from "lucide-react";
import { type ReactNode, useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverTitle,
  PopoverTrigger,
} from "@/shared/components/ui/popover";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { splitRecent } from "@/shared/lib/recent-split";

/** A partir deste tanto de itens a grade do "Anteriores" passa a rolar. */
const SCROLL_FROM = 20;

export type RecentPickerItem = {
  value: string;
  /** O texto do item no seletor. */
  label: string;
  /** O texto do botão "Anteriores" quando este item, que mora atrás dele, é o escolhido; o padrão é `label`. */
  shortLabel?: string;
  /** O conteúdo da célula do item na grade do "Anteriores". */
  cell: ReactNode;
  disabled?: boolean;
};

type RecentPickerProps = {
  /** Do mais antigo ao mais recente. */
  items: RecentPickerItem[];
  value: string;
  onChange: (value: string) => void;
  "aria-label": string;
  /** O título da grade: "Eleições da partida · 8". */
  title: string;
  /** O substantivo dos itens no plural, para a nota da rolagem. */
  noun: string;
  /** A frase que abre a nota no rodapé da grade. */
  description: string;
};

/** Seletor de uma lista cronológica: com 5 itens ou mais, os 3 recentes ficam à vista e o resto numa grade atrás do "Anteriores". */
export function RecentPicker({
  items,
  value,
  onChange,
  "aria-label": ariaLabel,
  title,
  noun,
  description,
}: RecentPickerProps) {
  const [open, setOpen] = useState(false);
  const { row, older } = splitRecent(items);
  const chosenOlder = older.find((item) => item.value === value);

  return (
    <ToggleGroup
      variant="segmented"
      aria-label={ariaLabel}
      data-own-arrows
      value={[chosenOlder ? "older" : value]}
      onValueChange={(next) => {
        if (next[0] && next[0] !== "older") onChange(next[0]);
      }}
    >
      {older.length > 0 && (
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger render={<ToggleGroupItem value="older" />}>
            {chosenOlder ? (chosenOlder.shortLabel ?? chosenOlder.label) : `Anteriores · ${older.length}`}
            <ChevronDown className="size-3.5" />
          </PopoverTrigger>
          <PopoverContent align="start" className="w-114">
            <div className="flex items-baseline justify-between">
              <PopoverTitle>{title}</PopoverTitle>
              <span className="text-xs text-muted-foreground">Esc fecha</span>
            </div>
            <div className={cn("grid grid-cols-4 gap-2", items.length >= SCROLL_FROM && "max-h-64 overflow-y-auto")}>
              {items.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  disabled={item.disabled}
                  aria-pressed={item.value === value}
                  onClick={() => {
                    onChange(item.value);
                    setOpen(false);
                  }}
                  className="flex flex-col items-start gap-1 rounded-lg border bg-card px-2.5 py-2 text-left transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50 aria-pressed:border-primary aria-pressed:bg-info-soft"
                >
                  {item.cell}
                </button>
              ))}
            </div>
            <PopoverDescription>
              {description} A partir de {SCROLL_FROM} {noun} a lista rola.
            </PopoverDescription>
          </PopoverContent>
        </Popover>
      )}
      {row.map((item) => (
        <ToggleGroupItem key={item.value} value={item.value} disabled={item.disabled}>
          {item.label}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
