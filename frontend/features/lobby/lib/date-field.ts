const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;
const BR_DATE = /^(\d{2})\/(\d{2})\/(\d{4})$/;

/** 31/02 não existe: a data volta igual quando montada pelo calendário. */
function isRealDate(year: number, month: number, day: number): boolean {
  const date = new Date(year, month - 1, day);
  return date.getFullYear() === year && date.getMonth() === month - 1 && date.getDate() === day;
}

export function isIsoDate(value: string): boolean {
  const match = ISO_DATE.exec(value);
  return match !== null && isRealDate(Number(match[1]), Number(match[2]), Number(match[3]));
}

/** "01042020" vira "01/04/2020": só dígitos, até 8, com as barras entrando sozinhas. */
export function maskDate(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

/**
 * O valor do campo é ISO quando a data digitada está completa e existe; antes disso
 * guarda o texto digitado, que o schema do formulário recusa com a mensagem certa.
 */
export function dateFieldValue(masked: string): string {
  const match = BR_DATE.exec(masked);
  if (!match) return masked;
  const [, day, month, year] = match;
  return isRealDate(Number(year), Number(month), Number(day)) ? `${year}-${month}-${day}` : masked;
}

/** O que o campo mostra: ISO vira dd/mm/aaaa, texto em digitação aparece como está. */
export function dateFieldDisplay(value: string): string {
  const match = ISO_DATE.exec(value);
  return match ? `${match[3]}/${match[2]}/${match[1]}` : value;
}

/** Mensagem de erro do campo; `null` quando está vazio (outra regra cobra) ou válido. */
export function dateFieldError(value: string): string | null {
  if (!value || isIsoDate(value)) return null;
  return BR_DATE.test(value) ? "Essa data não existe" : "Use dd/mm/aaaa";
}
