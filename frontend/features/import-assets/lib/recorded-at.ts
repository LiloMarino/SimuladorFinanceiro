const DAY_MS = 1000 * 60 * 60 * 24;
const startOfDay = (date: Date) => new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();

/** "hoje, 10:42", "ontem, 18:05" ou "17/10/2026, 09:30". */
export function displayRecordedAt(iso: string): string {
  const at = new Date(iso);
  const time = new Intl.DateTimeFormat("pt-BR", { hour: "2-digit", minute: "2-digit" }).format(at);
  const daysAgo = Math.round((startOfDay(new Date()) - startOfDay(at)) / DAY_MS);
  if (daysAgo === 0) return `hoje, ${time}`;
  if (daysAgo === 1) return `ontem, ${time}`;
  return `${new Intl.DateTimeFormat("pt-BR").format(at)}, ${time}`;
}
