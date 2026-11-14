import { normalizeNumberString } from "@/shared/lib/utils";
import { displayDecimal } from "@/shared/lib/utils/display";

export const FUND_FEE_CAP_MESSAGE = "O teto fica entre 0% e 100%";

/** "0.02" do servidor → "2" do campo (percentual). */
export const feeCapToField = (fraction: string) => displayDecimal(Number(fraction) * 100);

/** O campo guarda o percentual que o host digita ("2" é 2%); aqui vira fração. */
export const feeCapFraction = (field: string) => Number(normalizeNumberString(field)) / 100;

/** O teto de taxa como fração entre 0 e 1, a faixa que o servidor aceita. */
export const isFeeCap = (field: string) => {
  const fraction = feeCapFraction(field);
  return field !== "" && fraction >= 0 && fraction <= 1 + 1e-9;
};

/** O teto no corpo da API: fração com quatro casas ("2" → "0.0200"). */
export const feeCapToBody = (field: string) => feeCapFraction(field).toFixed(4);

/** Patrimônio e rendimento do exemplo que acompanha cada teto de taxa. */
const EXAMPLE_NET_WORTH = 1_000_000;
const EXAMPLE_YIELD = 0.15;
const EXAMPLE_CDI = 0.1;

/** Quanto o gestor recebe por mês de um patrimônio de R$ 1 milhão com o teto digitado (administração é ao ano, cobrada em 12 parcelas). */
export function managementFeeExample(field: string) {
  if (!isFeeCap(field)) return null;
  return (EXAMPLE_NET_WORTH * feeCapFraction(field)) / 12;
}

/** A parte do lucro acima do CDI que o gestor leva com o teto digitado: o exemplo rende 15% num CDI de 10%. */
export function performanceFeeExample(field: string) {
  if (!isFeeCap(field)) return null;
  const extraPoints = (EXAMPLE_YIELD - EXAMPLE_CDI) * 100;
  return { extraPoints, share: feeCapFraction(field), points: extraPoints * feeCapFraction(field) };
}
