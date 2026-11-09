/**
 * Quanto o dólar precisa subir em 12 meses para a conta em dólar render o mesmo que o CDI:
 * (1 + CDI) / (1 + Fed) − 1. Abaixo disso, ficar no CDI rende mais; acima, a conta ganha.
 */
export function breakEvenDollarRise(cdi: string, fed: string) {
  return (1 + Number(cdi)) / (1 + Number(fed)) - 1;
}

/** O que sobra de uma aplicação em reais depois do IOF do câmbio, e os dólares que isso compra. */
export function dollarPurchase(reais: number, dollar: number, fxIofRate: string) {
  const iof = reais * Number(fxIofRate);
  return { iof, dollars: (reais - iof) / dollar };
}
