/** Quem passa de metade das cotas governa a gestora. */
export const CONTROL_SHARE = 0.5;

/** Cotas necessárias para ter mais da metade do total. */
const controlThreshold = (total: number) => Math.floor(total * CONTROL_SHARE) + 1;

/** Quantas cotas faltam para o controle (0 quando já controla). */
export function quotasToControl(mine: number, total: number) {
  return Math.max(0, controlThreshold(total) - mine);
}

/** Quantas cotas o gestor vende sem cair abaixo do controle. */
export function sellableKeepingControl(mine: number, total: number) {
  return Math.max(0, Math.floor(mine - controlThreshold(total)));
}

/** Ágio (positivo) ou deságio (negativo) do preço sobre o patrimônio por cota, como fração. */
export function premium(price: number, nav: number) {
  return nav > 0 ? price / nav - 1 : 0;
}
