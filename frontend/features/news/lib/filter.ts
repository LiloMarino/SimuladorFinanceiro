import type { News, NewsLevel, NewsSection, NewsType } from "@/types";

export type JournalFilter = {
  query: string;
  section: NewsSection | null;
  /** Só as manchetes que citam um ativo da carteira */
  onlyMine: boolean;
};

type FilterContext = {
  /** A seção de cada tipo, pelo registro */
  sectionOf: (type: NewsType) => NewsSection | undefined;
  /** O nível da manchete para o jogador, com o filtro de carteira já aplicado */
  levelOf: (item: News) => NewsLevel | undefined;
  held: ReadonlySet<string>;
};

/**
 * O nível que o jogador dá à manchete: o do tipo, ou desligado quando o tipo só vale para ativos da
 * carteira e a manchete não cita nenhum deles.
 */
export function levelFor<Level extends NewsLevel | undefined>(
  level: Level,
  onlyHeld: boolean,
  tickers: readonly string[],
  held: ReadonlySet<string>,
): Level | "OFF" {
  return onlyHeld && !tickers.some((ticker) => held.has(ticker)) ? "OFF" : level;
}

/** O que a página do jornal mostra: o tipo desligado fica de fora; o resto passa pela busca, pela seção e pela carteira. */
export function filterNews(items: News[], filter: JournalFilter, { sectionOf, levelOf, held }: FilterContext) {
  const query = filter.query.trim().toLocaleLowerCase("pt-BR");
  return items.filter((item) => {
    if (levelOf(item) === "OFF") return false;
    if (filter.section !== null && sectionOf(item.news_type) !== filter.section) return false;
    if (filter.onlyMine && !item.tickers.some((ticker) => held.has(ticker))) return false;
    if (query === "") return true;
    const text = [item.headline, item.dek ?? "", ...item.tickers].join(" ").toLocaleLowerCase("pt-BR");
    return text.includes(query);
  });
}

/** As manchetes agrupadas por dia, na ordem em que chegaram (da mais nova para a mais antiga). */
export function groupByDay(items: News[]) {
  const groups: { day: string; items: News[] }[] = [];
  for (const item of items) {
    const last = groups[groups.length - 1];
    if (last?.day === item.news_date) last.items.push(item);
    else groups.push({ day: item.news_date, items: [item] });
  }
  return groups;
}
