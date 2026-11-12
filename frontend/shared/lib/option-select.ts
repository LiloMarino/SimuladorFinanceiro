// A busca aparece a partir de 8 opções: abaixo disso a lista inteira cabe na vista
const SEARCH_THRESHOLD = 8;

// Opção bloqueada com motivo escrito vai para o grupo "Indisponíveis"; sem motivo, fica no lugar
type Blockable = { disabled?: boolean | undefined; reason?: string | undefined };

type SearchableOption = { label: string; description?: string | undefined; searchText?: string | undefined };

const normalize = (text: string) =>
  text
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim();

export const shouldShowSearch = (optionCount: number, forced?: boolean) => forced ?? optionCount >= SEARCH_THRESHOLD;

const isUnavailable = (option: Blockable) => Boolean(option.disabled && option.reason);

// Separa as opções livres das indisponíveis, mantendo a ordem de cada grupo
export function splitUnavailable<T extends Blockable>(options: readonly T[]) {
  return {
    available: options.filter((option) => !isUnavailable(option)),
    unavailable: options.filter(isUnavailable),
  };
}

// A busca ignora acento e caixa e olha o rótulo, a descrição e o texto extra (código + nome da ação)
export function matchesQuery(option: SearchableOption, query: string) {
  const needle = normalize(query);
  if (!needle) return true;
  const haystack = [option.label, option.description, option.searchText].filter(Boolean).join(" ");
  return normalize(haystack).includes(needle);
}

export const isAtLimit = (selected: readonly string[], max: number | null) => max !== null && selected.length >= max;
