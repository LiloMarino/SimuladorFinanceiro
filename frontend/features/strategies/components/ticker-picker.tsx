import { Button } from "@/shared/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/shared/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";

type TickerPickerProps = {
  options: string[];
  selected: string[];
  onChange: (tickers: string[]) => void;
};

/** "Escolher": marca e desmarca as ações da lista; a escolha sai na ordem das opções. */
export function TickerPicker({ options, selected, onChange }: TickerPickerProps) {
  const toggle = (ticker: string) => {
    const next = new Set(selected);
    if (!next.delete(ticker)) next.add(ticker);
    onChange(options.filter((option) => next.has(option)));
  };

  return (
    <Popover>
      <PopoverTrigger render={<Button variant="link" size="sm" />}>Escolher</PopoverTrigger>
      <PopoverContent align="end" className="w-64">
        <Command>
          <CommandInput placeholder="Buscar ação" />
          <CommandList>
            <CommandEmpty>Nenhuma ação encontrada.</CommandEmpty>
            <CommandGroup>
              {options.map((ticker) => (
                <CommandItem
                  key={ticker}
                  value={ticker}
                  selected={selected.includes(ticker)}
                  onSelect={() => toggle(ticker)}
                >
                  <span className="font-mono font-semibold">{ticker}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
