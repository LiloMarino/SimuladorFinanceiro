import { useState } from "react";
import { useDebounce } from "use-debounce";
import { Command, CommandItem, CommandList } from "@/shared/components/ui/command";
import { Input } from "@/shared/components/ui/input";
import { useTickerSearch } from "../hooks/queries/useTickerSearch";

type TickerComboboxProps = {
  id: string;
  value: string;
  onChange: (ticker: string) => void;
  /** Liga a lista de códigos do yFinance; desligada, o campo é só um campo de texto */
  suggest: boolean;
  placeholder?: string;
  invalid?: boolean;
  disabled?: boolean;
};

const MIN_CHARS = 2;

/** Campo de código com a lista de códigos da B3 e o nome da empresa. A lista só sugere: o texto digitado continua valendo. */
export function TickerCombobox({ id, value, onChange, suggest, placeholder, invalid, disabled }: TickerComboboxProps) {
  const [open, setOpen] = useState(false);
  const [debounced] = useDebounce(value.trim(), 300);

  const enabled = suggest && debounced.length >= MIN_CHARS;
  const { data: suggestions = [] } = useTickerSearch(debounced, { enabled });

  const showList = open && enabled && suggestions.length > 0;

  const choose = (ticker: string) => {
    onChange(ticker);
    setOpen(false);
  };

  return (
    <Command
      shouldFilter={false}
      loop
      className="relative overflow-visible"
      onKeyDown={(e) => {
        if (e.key === "Escape" && showList) {
          e.stopPropagation();
          setOpen(false);
        }
      }}
    >
      <Input
        id={id}
        numeric
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        placeholder={placeholder}
        aria-invalid={invalid}
        aria-autocomplete="list"
        autoComplete="off"
        disabled={disabled}
      />
      {showList && (
        // O mouse-down não tira o foco do campo, senão o onBlur fecha a lista antes do clique
        <div
          className="absolute inset-x-0 top-full z-50 mt-1 rounded-lg bg-popover shadow-md ring-1 ring-foreground/10"
          onMouseDown={(e) => e.preventDefault()}
        >
          <CommandList>
            {suggestions.map((item) => (
              <CommandItem key={item.ticker} value={item.ticker} onSelect={() => choose(item.ticker)}>
                <span className="font-mono">{item.ticker}</span>
                <span className="truncate text-muted-foreground">{item.name}</span>
              </CommandItem>
            ))}
          </CommandList>
        </div>
      )}
    </Command>
  );
}
