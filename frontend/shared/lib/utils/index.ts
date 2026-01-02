import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function isSameSet(a: Set<unknown>, b: Set<unknown>): boolean {
  if (a.size !== b.size) return false;
  for (const value of a) {
    if (!b.has(value)) return false;
  }
  return true;
}

export function stringToColor(str: string) {
  let hash = 0;

  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, 60%, 55%)`;
}

export function normalizeNumberString(value?: string): string {
  if (!value) return "";

  return (
    value
      // Remove espaços no início e no fim
      .trim()

      // Remove todos os tipo de whitespace (espaço, tab, quebra de linha)
      // Ex: "1 234 , 56" → "1234,56"
      .replace(/\s/g, "")

      // Remove qualquer caractere que NÃO seja:
      // - dígito (0–9)
      // - vírgula (separador decimal pt-BR)
      // - ponto (possível separador de milhar)
      // - hífen (sinal negativo)
      // Ex: "R$ -1.234,56%" → "-1.234,56"
      .replace(/[^\d,.-]/g, "")

      // Remove pontos que representem separador de milhar
      // Critério: ponto seguido imediatamente por 3 dígitos
      // Ex: "1.234" → "1234"
      // Ex: "12.345.678" → "12345678"
      // Não remove ponto decimal (ex: "123.45")
      .replace(/\.(?=\d{3})/g, "")

      // Converte vírgula decimal (pt-BR) em ponto decimal (JS)
      // Ex: "1234,56" → "1234.56"
      .replace(",", ".")
  );
}
