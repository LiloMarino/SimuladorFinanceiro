import { useState } from "react";
import { EraserIcon, RotateCcwIcon, WalletIcon, XIcon } from "lucide-react";
import { DisabledHint } from "@/shared/components/disabled-hint";
import type { SelectOption } from "@/shared/components/option-select";
import { Button } from "@/shared/components/ui/button";
import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxItem,
  ComboboxList,
  ComboboxTrigger,
} from "@/shared/components/ui/combobox";
import { isAtLimit, matchesQuery } from "@/shared/lib/option-select";
import { inOptionOrder, sameTickerSet, tickerOption } from "@/shared/lib/strategy-params";
import { cn } from "@/shared/lib/utils";
import type { BotTicker } from "@/types";

const SEARCH_PLACEHOLDER = "Buscar ação por código ou nome";

const filterOption = (option: SelectOption, query: string) => matchesQuery(option, query);

type TickerPickerProps = {
  options: readonly BotTicker[];
  selected: readonly string[];
  /** A escolha padrão da estratégia, para o "Voltar ao padrão" */
  standard: readonly string[];
  /** Teto de ações marcadas; `null` quando não há */
  max: number | null;
  /** Ações da carteira; `undefined` antes da partida, quando não há carteira */
  held: readonly string[] | undefined;
  invalid: boolean;
  id?: string;
  onChange: (tickers: string[]) => void;
};

/** Ações que a estratégia opera: botão com a contagem, lista que fica aberta enquanto marca, etiquetas e atalhos. */
export function TickerPicker({ options, selected, standard, max, held, invalid, id, onChange }: TickerPickerProps) {
  // A consulta é só o que a pessoa digita; cada abertura da lista começa vazia
  const [query, setQuery] = useState("");
  const items = options.map(tickerOption);
  const selectedSet = new Set(selected);
  const chosen = items.filter((item) => selectedSet.has(item.value));
  const atLimit = isAtLimit(selected, max);
  const isStandard = sameTickerSet(selected, standard);
  const heldHere = held ? inOptionOrder(options, held) : [];
  const empty = options.length === 0;

  const commit = (tickers: readonly string[]) => onChange(inOptionOrder(options, tickers));

  return (
    <>
      <Combobox
        multiple
        items={items}
        filter={filterOption}
        value={chosen}
        onValueChange={(next: SelectOption[]) => commit(next.map((item) => item.value))}
        isItemEqualToValue={(a: SelectOption, b: SelectOption) => a.value === b.value}
        disabled={empty}
        inputValue={query}
        onInputValueChange={(next, details) => {
          if (details.reason === "input-change" || details.reason === "input-clear") setQuery(next);
        }}
        onOpenChange={() => setQuery("")}
      >
        <ComboboxTrigger id={id} aria-invalid={invalid || undefined} className="w-full">
          {empty ? (
            <span className="text-muted-foreground">Nenhuma ação nesta partida</span>
          ) : selected.length === 0 ? (
            <span className="text-muted-foreground">Nenhuma ação marcada</span>
          ) : (
            <>
              <span className="font-medium">
                ações <span className="font-mono font-semibold">{selected.length}</span>
              </span>
              {(atLimit || isStandard) && (
                <span className={cn("font-normal", atLimit ? "text-warning" : "text-muted-foreground")}>
                  · {atLimit ? "limite" : "padrão"}
                </span>
              )}
            </>
          )}
        </ComboboxTrigger>
        <ComboboxContent search={SEARCH_PLACEHOLDER} className="w-(--anchor-width) max-w-none min-w-64">
          {atLimit ? (
            <div className="-mx-1 mb-1 bg-warning-soft px-3.5 py-2.5 text-[13px] leading-[18px] text-warning">
              <b className="font-mono font-semibold">{selected.length}</b> de {max} marcadas · desmarque uma para trocar
            </div>
          ) : (
            <div className="px-2.5 pt-2 pb-1.5 text-[13px] text-muted-foreground">
              <b className="font-mono font-semibold text-foreground">{selected.length}</b>
              {max !== null ? ` de ${max} marcadas` : " marcadas"}
            </div>
          )}
          <ComboboxEmpty>Nenhuma ação encontrada.</ComboboxEmpty>
          <ComboboxList>
            {(item: SelectOption) => (
              <ComboboxItem
                key={item.value}
                value={item}
                indicator="checkbox"
                disabled={atLimit && !selectedSet.has(item.value)}
              >
                <span className="min-w-0 flex-1 [overflow-wrap:anywhere]">
                  <span className="block font-mono font-semibold">{item.label}</span>
                  <span className="block text-[13px] text-muted-foreground">{item.description}</span>
                </span>
              </ComboboxItem>
            )}
          </ComboboxList>
        </ComboboxContent>
      </Combobox>

      {/* Ações marcadas */}
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selected.map((ticker) => (
            <span
              key={ticker}
              className="inline-flex h-7 items-center gap-0.5 rounded-md bg-muted pr-0.5 pl-2 font-mono text-[13px] font-semibold"
            >
              {ticker}
              <button
                type="button"
                aria-label={`Tirar ${ticker}`}
                onClick={() => commit(selected.filter((item) => item !== ticker))}
                className="flex size-6 items-center justify-center rounded-sm text-muted-foreground hover:bg-border hover:text-foreground"
              >
                <XIcon className="size-3.5" aria-hidden />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Atalhos */}
      <div className="flex flex-wrap gap-2">
        <DisabledHint reason={held === undefined ? "Antes da partida não há carteira" : null}>
          <Button
            variant="outline"
            size="sm"
            disabled={heldHere.length === 0}
            onClick={() => commit(heldHere.slice(0, max ?? undefined))}
          >
            <WalletIcon aria-hidden />
            Só as da carteira
            {held !== undefined && <span className="font-mono text-muted-foreground">· {heldHere.length}</span>}
          </Button>
        </DisabledHint>
        <Button variant="outline" size="sm" disabled={isStandard || empty} onClick={() => commit(standard)}>
          <RotateCcwIcon aria-hidden />
          Voltar ao padrão
        </Button>
        <Button variant="outline" size="sm" disabled={selected.length === 0} onClick={() => onChange([])}>
          <EraserIcon aria-hidden />
          Limpar
        </Button>
      </div>
    </>
  );
}
