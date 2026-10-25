export interface SeriesPoint {
  date: string;
  value: number;
}

export interface Crossover {
  /** O primeiro dia em que `a` passou para o outro lado de `b`. */
  date: string;
  /** `up`: `a` cruzou para cima de `b`. */
  direction: "up" | "down";
}

/**
 * Os dias em que a série `a` cruza a `b`. Compara só os dias que as duas têm; empate
 * (a = b) herda o lado do dia anterior, então um toque sem virar não conta.
 */
export function crossovers(a: SeriesPoint[], b: SeriesPoint[]): Crossover[] {
  const bByDate = new Map(b.map((point) => [point.date, point.value]));
  const found: Crossover[] = [];
  let side = 0;

  for (const point of a) {
    const other = bByDate.get(point.date);
    if (other === undefined) continue;
    const diff = point.value - other;
    if (diff === 0) continue;
    const now = diff > 0 ? 1 : -1;
    if (side !== 0 && now !== side) found.push({ date: point.date, direction: now > 0 ? "up" : "down" });
    side = now;
  }
  return found;
}
