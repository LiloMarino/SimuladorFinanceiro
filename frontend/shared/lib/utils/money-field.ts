import { normalizeNumberString } from "@/shared/lib/utils";
import { toCentsString } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";

/** O dinheiro do servidor como o campo mostra ("R$ 1.000,00"). */
export const moneyToField = (value: string) => formatMoney(toCentsString(value));

/** O que o campo mostra como dinheiro do servidor (centavos em texto). */
export const moneyToBody = (field: string) => toCentsString(normalizeNumberString(field));
