import { displayMoneyCompact, displayMoneyLarge } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";

const BILLION = 1e9;

/** Os atalhos do aporte, em bilhões de reais, até o teto de R$ 500 bi por aporte: cada um troca o valor do campo. */
export const CONTRIBUTION_SHORTCUTS_BILLIONS = [25, 100, 250, 500] as const;

/** O campo de valor preenchido com `billions` bilhões, em centavos inteiros. */
export const billionsToField = (billions: number) => formatMoney(String(billions * BILLION * 100));

/** "R$ 25 bi" no rótulo do atalho. */
export const shortcutLabel = (billions: number) => displayMoneyCompact(billions * BILLION);

/** O caixa do fundo como a tela lê: "R$ 18,4 bi" ou "R$ 0". */
export const fundCashLabel = (cash: string) => (Number(cash) === 0 ? "R$ 0" : displayMoneyLarge(cash));
