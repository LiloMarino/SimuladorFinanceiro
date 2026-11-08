import { normalizeNumberString } from "@/shared/lib/utils";
import { toCentsString } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";

/** O dinheiro do servidor como o campo mostra ("R$ 1.000,00"). */
export const moneyToField = (value: string) => formatMoney(toCentsString(value));

/** O que o campo mostra como dinheiro do servidor (centavos em texto). */
export const moneyToBody = (field: string) => toCentsString(normalizeNumberString(field));

/** Uma fração do total como o campo mostra, truncada nos centavos para nunca passar do total: (1000.01, 0.25) → "R$ 250,00". */
export const shareToField = (total: string | number, share: number) => moneyToField(String(Number(total) * share));
