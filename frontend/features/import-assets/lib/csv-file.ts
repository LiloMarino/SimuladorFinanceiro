const CSV_MAX_BYTES = 5 * 1024 * 1024;

/** O que se sabe do arquivo escolhido; `problem` preenchido quando ele não serve. */
export type CsvInspection = {
  file: File;
  problem: { title: string; hint: string } | null;
  /** Pregões e período do arquivo; vazio quando o conteúdo não foi lido */
  rows: number | null;
  from: Date | null;
  to: Date | null;
};

const REQUIRED_COLUMNS = ["Data", "Último"];

/** O CSV traz datas como dd.mm.aaaa, entre aspas ou não. */
function parseCsvDate(raw: string): Date | null {
  const match = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(raw.replaceAll('"', "").trim());
  if (!match) return null;
  return new Date(Number(match[3]), Number(match[2]) - 1, Number(match[1]));
}

/** Código do ativo tirado do nome do arquivo: "itsa4_2015-2026.csv" vira "ITSA4". */
export function tickerFromFileName(fileName: string): string {
  const match = /^([a-z]{4}\d{1,2}|[a-z]{3,6}-[a-z]{3})/i.exec(fileName);
  return match ? match[1].toUpperCase() : "";
}

/** Confere o arquivo no navegador antes de enviar: extensão, tamanho, colunas e período. */
export async function inspectCsv(file: File): Promise<CsvInspection> {
  const empty = { file, rows: null, from: null, to: null };

  if (!file.name.toLowerCase().endsWith(".csv")) {
    return {
      ...empty,
      problem: {
        title: `${file.name} não é CSV`,
        hint: "Salve a planilha como .csv, com as colunas separadas por vírgula, e tente de novo.",
      },
    };
  }
  if (file.size > CSV_MAX_BYTES) {
    return {
      ...empty,
      problem: { title: `${file.name} passa de 5 MB`, hint: "Corte o período do arquivo e tente de novo." },
    };
  }

  const lines = (await file.text()).split(/\r?\n/).filter((line) => line.trim() !== "");
  const header = (lines[0] ?? "").split(",").map((column) => column.replaceAll('"', "").trim());
  const missing = REQUIRED_COLUMNS.filter((column) => !header.includes(column));
  if (missing.length > 0) {
    return {
      ...empty,
      problem: {
        title: `${file.name} não tem a coluna ${missing.join(" nem ")}`,
        hint: "Confira se o arquivo tem o cabeçalho com Data, Último, Abertura, Máxima, Mínima e Vol.",
      },
    };
  }

  const dates = lines
    .slice(1)
    .map((line) => parseCsvDate(line.split(",")[header.indexOf("Data")] ?? ""))
    .filter((date): date is Date => date !== null)
    .sort((a, b) => a.getTime() - b.getTime());

  return { file, problem: null, rows: lines.length - 1, from: dates[0] ?? null, to: dates.at(-1) ?? null };
}
