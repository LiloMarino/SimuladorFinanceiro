import { useState, type ReactNode } from "react";
import { LockIcon, PlusIcon } from "lucide-react";
import {
  Combobox,
  ComboboxCollection,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxGroup,
  ComboboxGroupLabel,
  ComboboxItem,
  ComboboxList,
  ComboboxSeparator,
  ComboboxTrigger,
} from "@/shared/components/ui/combobox";
import { matchesQuery, shouldShowSearch, splitUnavailable } from "@/shared/lib/option-select";
import { cn } from "@/shared/lib/utils";

export type SelectOption<V extends string = string> = {
  value: V;
  label: string;
  // Segunda linha da opção (nome da empresa, partido)
  description?: string | undefined;
  // Marca à esquerda do texto (avatar, bandeira, cor)
  leading?: ReactNode | undefined;
  // Quantidade à direita, antes do ✓
  count?: number | undefined;
  // Texto curto do botão quando a opção está escolhida ("Todos" no botão, "Todos os setores" na lista)
  triggerLabel?: string | undefined;
  // Linha divisória acima da opção, para separar blocos da mesma lista
  dividerBefore?: boolean | undefined;
  disabled?: boolean | undefined;
  // Motivo escrito do bloqueio: a opção vai para o grupo "Indisponíveis" mostrando esta frase
  reason?: string | undefined;
  // Texto extra que a busca também olha
  searchText?: string | undefined;
  // Título da seção em que a opção aparece; opções com o mesmo título ficam juntas, na ordem em que surgem
  group?: string | undefined;
};

type OptionGroup<V extends string> = { value: string; label?: string; items: SelectOption<V>[] };

type OptionSelectProps<V extends string> = {
  options: readonly SelectOption<V>[];
  value: V | null;
  onChange: (value: V) => void;
  placeholder?: string;
  // Rótulo dentro do botão, antes do valor ("Setor")
  prefix?: string;
  // Força ou esconde a busca; sem isso ela aparece a partir de 8 opções
  search?: boolean;
  searchPlaceholder?: string;
  emptyText?: string;
  // Com isto, o que foi digitado e não existe vira a linha "Criar …" no fim da lista; a busca fica sempre à vista
  onCreate?: (text: string) => void;
  createLabel?: (text: string) => string;
  invalid?: boolean;
  disabled?: boolean;
  onBlur?: () => void;
  id?: string;
  "aria-label"?: string;
  className?: string;
};

const UNAVAILABLE_LABEL = "Indisponíveis";

const CREATE_PREFIX = "__create__";

// A linha "Criar …" acompanha qualquer digitação; as demais seguem a busca
const filterOption = (option: SelectOption, query: string) =>
  option.value.startsWith(CREATE_PREFIX) || matchesQuery(option, query);

function sectionsOf<V extends string>(available: SelectOption<V>[], unavailable: SelectOption<V>[]) {
  const sections: OptionGroup<V>[] = [];
  const loose = available.filter((option) => !option.group);
  if (loose.length > 0) sections.push({ value: "loose", items: loose });
  for (const title of new Set(available.map((option) => option.group).filter((title) => title !== undefined))) {
    sections.push({
      value: `group:${title}`,
      label: title,
      items: available.filter((option) => option.group === title),
    });
  }
  if (unavailable.length > 0) sections.push({ value: "unavailable", label: UNAVAILABLE_LABEL, items: unavailable });
  return sections;
}

function OptionRow({ option }: { option: SelectOption }) {
  return (
    <>
      {option.dividerBefore && <ComboboxSeparator />}
      <ComboboxItem value={option} disabled={option.disabled}>
        {option.reason ? <LockIcon className="size-4 shrink-0 text-muted-foreground" aria-hidden /> : option.leading}
        <span className="min-w-0 flex-1 [overflow-wrap:anywhere]">
          <span className="block group-aria-selected/item:font-medium">{option.label}</span>
          {option.description && <span className="block text-[13px] text-muted-foreground">{option.description}</span>}
          {option.reason && (
            <span className="mt-0.5 block text-xs leading-4 text-muted-foreground">{option.reason}</span>
          )}
        </span>
        {option.count !== undefined && (
          <span className="font-mono text-[13px] text-muted-foreground tabular-nums">{option.count}</span>
        )}
      </ComboboxItem>
    </>
  );
}

export function OptionSelect<V extends string>({
  options,
  value,
  onChange,
  placeholder = "Selecione",
  prefix,
  search,
  searchPlaceholder = "Buscar",
  emptyText = "Nada encontrado.",
  onCreate,
  createLabel = (text) => `Criar “${text}”`,
  invalid,
  disabled,
  onBlur,
  id,
  "aria-label": ariaLabel,
  className,
}: OptionSelectProps<V>) {
  // A consulta é só o que a pessoa digita: escolher uma opção não a preenche com o rótulo e cada abertura começa vazia
  const [query, setQuery] = useState("");
  const selected = options.find((option) => option.value === value) ?? null;
  const typed = query.trim();
  const canCreate =
    onCreate !== undefined &&
    typed !== "" &&
    !options.some((option) => option.label.toLowerCase() === typed.toLowerCase());
  const createOption = canCreate
    ? ({
        value: `${CREATE_PREFIX}${typed}`,
        label: createLabel(typed),
        leading: <PlusIcon className="size-4 shrink-0 text-primary" aria-hidden />,
      } as SelectOption<V>)
    : null;
  const split = splitUnavailable(options);
  const available = createOption ? [...split.available, createOption] : split.available;
  const { unavailable } = split;
  // Seções por título e, no fim, as indisponíveis; sem nenhum dos dois, uma lista só
  const sectioned = unavailable.length > 0 || available.some((option) => option.group);
  const items: readonly SelectOption<V>[] | readonly OptionGroup<V>[] = sectioned
    ? sectionsOf(available, unavailable)
    : available;

  return (
    <Combobox
      items={items}
      filter={filterOption}
      value={selected}
      onValueChange={(next: SelectOption<V> | null) => {
        if (!next) return;
        if (next.value.startsWith(CREATE_PREFIX)) onCreate?.(next.value.slice(CREATE_PREFIX.length));
        else onChange(next.value);
      }}
      isItemEqualToValue={(a: SelectOption<V>, b: SelectOption<V>) => a.value === b.value}
      disabled={disabled}
      inputValue={query}
      onInputValueChange={(next, details) => {
        if (details.reason === "input-change" || details.reason === "input-clear") setQuery(next);
      }}
      onOpenChange={() => setQuery("")}
    >
      <ComboboxTrigger
        id={id}
        aria-label={ariaLabel}
        aria-invalid={invalid || undefined}
        onBlur={onBlur}
        className={className}
      >
        {prefix && <span className="shrink-0 text-muted-foreground">{prefix}</span>}
        {selected?.leading}
        <span className={cn("min-w-0 truncate", selected ? "font-medium" : "text-muted-foreground")}>
          {selected ? (selected.triggerLabel ?? selected.label) : placeholder}
        </span>
      </ComboboxTrigger>
      <ComboboxContent
        search={
          shouldShowSearch(options.length, search ?? (onCreate ? true : undefined)) ? searchPlaceholder : undefined
        }
      >
        <ComboboxEmpty>{emptyText}</ComboboxEmpty>
        <ComboboxList>
          {(entry: SelectOption<V> | OptionGroup<V>) =>
            "items" in entry ? (
              <ComboboxGroup key={entry.value} items={entry.items}>
                {entry.label !== undefined && (
                  <>
                    {entry.value !== items[0]?.value && <ComboboxSeparator />}
                    <ComboboxGroupLabel>{entry.label}</ComboboxGroupLabel>
                  </>
                )}
                <ComboboxCollection>
                  {(option: SelectOption<V>) => <OptionRow key={option.value} option={option} />}
                </ComboboxCollection>
              </ComboboxGroup>
            ) : (
              <OptionRow key={entry.value} option={entry} />
            )
          }
        </ComboboxList>
      </ComboboxContent>
    </Combobox>
  );
}
