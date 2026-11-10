import { displayQuantity } from "@/shared/lib/utils/display";

/** Quantos salários, da string decimal da API: "1.00" → "1 salário", "2.35" → "2,35 salários". */
export function salariesLabel(salaries: string | number) {
  const text = displayQuantity(String(salaries));
  return `${text} ${Number(salaries) === 1 ? "salário" : "salários"}`;
}
