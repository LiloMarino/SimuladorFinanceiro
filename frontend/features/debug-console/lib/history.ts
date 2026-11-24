export interface HistoryStep {
  /** A posição no histórico; igual ao tamanho dele quando o campo está na linha nova. */
  readonly cursor: number;
  readonly line: string;
}

/** Uma passada das setas: para cima volta nos comandos enviados, para baixo avança até a linha vazia. */
export function stepHistory(entries: readonly string[], cursor: number, direction: "up" | "down"): HistoryStep {
  if (direction === "up") {
    const next = Math.max(cursor - 1, 0);
    return { cursor: next, line: entries[next] ?? "" };
  }
  const next = cursor + 1;
  if (next >= entries.length) return { cursor: entries.length, line: "" };
  return { cursor: next, line: entries[next] ?? "" };
}
