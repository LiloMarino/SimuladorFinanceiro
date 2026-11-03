import { displayMonthName } from "@/shared/lib/utils/display";

/** Um mês no formato AAAA-MM, o mesmo que o endpoint de manchetes recebe. */
export type Month = string;

export type ArchiveYear = {
  year: number;
  /** Os meses do ano que a partida já viveu, do mais novo para o mais antigo */
  months: Month[];
};

/** O mês de uma data ISO (AAAA-MM-DD). */
export function monthOf(date: string): Month {
  return date.slice(0, 7);
}

/** O mês anterior, virando o ano em janeiro. */
export function previousMonth(month: Month): Month {
  const year = Number(month.slice(0, 4));
  const number = Number(month.slice(5, 7));
  return number === 1 ? `${year - 1}-12` : `${year}-${String(number - 1).padStart(2, "0")}`;
}

/** Os meses da partida, do primeiro ao atual, agrupados por ano (o ano mais novo primeiro). */
export function archiveMonths(startMonth: Month, currentMonth: Month): ArchiveYear[] {
  const years: ArchiveYear[] = [];
  for (let month = currentMonth; month >= startMonth; month = previousMonth(month)) {
    const year = Number(month.slice(0, 4));
    const last = years.at(-1);
    if (last?.year === year) last.months.push(month);
    else years.push({ year, months: [month] });
  }
  return years;
}

/** "2030-10" → "outubro de 2030", o mês por extenso. */
export function monthLabel(month: Month): string {
  return `${displayMonthName(`${month}-01`)} de ${month.slice(0, 4)}`;
}
