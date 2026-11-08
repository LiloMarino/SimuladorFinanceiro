/** O topo de um dia da lista, medido do topo da janela. */
export type DaySection = { day: string; top: number };

/**
 * O dia em leitura: o último cujo título já chegou à linha de leitura (logo abaixo do topo fixo).
 * As seções vêm na ordem da página; `null` quer dizer que nenhum dia anterior chegou lá e "Hoje" está na tela.
 */
export function readingDay(sections: DaySection[], line: number): string | null {
  let current: string | null = null;
  for (const section of sections) {
    if (section.top > line) break;
    current = section.day;
  }
  return current;
}
