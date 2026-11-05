import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayPercent } from "@/shared/lib/utils/display";

const percent = (value: string | number) => displayPercent(value, 2);

export const SELIC: MetricInfo = {
  label: "SELIC",
  description: "O juro básico da economia, ao ano",
  definition:
    "A taxa que o Banco Central fixa e que serve de base para todos os outros juros: o CDI, os títulos do Tesouro, o crédito. Ela só muda nas reuniões do Copom.",
  example: "Ex.: com a SELIC a 10% ao ano, R$ 100 parados nela viram R$ 110 em um ano.",
  reading:
    "Quanto mais alta, mais a renda fixa rende e mais caro fica o crédito. O Copom costuma subi-la quando a inflação passa da meta e baixá-la quando a inflação cede.",
  format: percent,
};

export const IPCA: MetricInfo = {
  label: "IPCA em 12 meses",
  description: "A inflação oficial, acumulada no último ano",
  definition: "O quanto os preços subiram nos últimos 12 meses, medido pelo índice oficial do país.",
  example: "Ex.: 5% em 12 meses quer dizer que o que custava R$ 100 há um ano custa R$ 105 hoje.",
  reading:
    "Dentro da meta do ano é o bom sinal; acima dela, o dinheiro perde poder de compra e o governo perde aprovação.",
  format: percent,
};

export const REAL_RATE: MetricInfo = {
  label: "Juro real",
  description: "Quanto o dinheiro rende de verdade, descontada a inflação",
  definition: "A SELIC menos o IPCA de 12 meses: o rendimento que sobra depois de a inflação comer parte dele.",
  example: "Ex.: SELIC de 10% com inflação de 4% dá juro real de 6%; R$ 100 viram R$ 106 em poder de compra.",
  reading:
    "Positivo, guardar dinheiro na renda fixa ganha da inflação; negativo, perde. Acima de uns 7% esfria a economia; perto de zero ou negativo, aquece e puxa a inflação.",
  format: percent,
};

export const IBOVESPA: MetricInfo = {
  label: "Ibovespa",
  description: "O índice das ações mais negociadas da bolsa, em pontos",
  definition:
    "Uma média do preço das maiores ações da bolsa, em pontos. Sobe quando a bolsa em geral sobe e cai quando ela cai. Aqui ele já conta o efeito do governo: cada ponto de SELIC ou de prêmio de risco a mais tira 2,9% da bolsa no trimestre, e o PIB acima da história a levanta.",
  example: "Ex.: de 78.800 para 75.700 pontos é uma queda de 3,9%: uma carteira que acompanha a bolsa perde 3,9%.",
  reading: "Mais alto é bom para quem tem ações. Compare com a história ao lado: a diferença é o que o governo fez.",
  format: (value) => Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 0 }),
};

export const EFFECT_IPCA = {
  definition:
    "Quantos pontos a medida ou a ligação soma hoje ao IPCA de 12 meses. O efeito da medida chega meses depois de ela valer, fica cheio e cai pela metade a cada 12 meses; o da ligação segue o desvio do último mês fechado.",
  example: "Ex.: +0,55 com o IPCA da história em 2,40% leva a inflação da partida a 2,95%.",
  reading:
    "Vermelho é inflação a mais; verde, a menos. Zero ou traço quer dizer que o efeito ainda não chegou ou já sumiu.",
};

export const EFFECT_SELIC = {
  definition:
    "O quanto o Banco Central sobe (ou corta) a SELIC por causa da inflação que a medida ou a ligação soma: 1,5 vez o tanto.",
  example: "Ex.: +0,55 ponto de inflação leva a +0,83 ponto de SELIC (0,55 × 1,5).",
  reading: "SELIC mais alta encarece o crédito e faz a renda fixa render mais; menos crescimento no curto prazo.",
};

export const EFFECT_STOCKS = {
  definition:
    "Quanto a bolsa anda no trimestre por causa da medida ou da ligação: cada ponto de SELIC ou de prêmio de risco a mais tira 2,9% da bolsa, e ações de beta alto (que se mexem mais que o Ibovespa) sentem mais.",
  example: "Ex.: +0,83 ponto de SELIC tira uns 2,4% do Ibovespa no trimestre.",
  reading: "Negativo, a bolsa cai por causa dela; positivo, sobe. Vale para toda ação, ajustada pelo beta dela.",
};

const POINTS = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** Fração em pontos com sinal e uma casa: 0.012 → "+1,2". */
export function signedPoints(fraction: number) {
  const points = Math.round(fraction * 1000) / 10;
  if (points === 0) return POINTS.format(0);
  return `${points < 0 ? "−" : "+"}${POINTS.format(Math.abs(points))}`;
}

const gapPoints = (value: string | number) =>
  `${signedPoints(Number(value))} ponto${Math.abs(Number(value)) >= 0.0195 ? "s" : ""}`;

export const PHILLIPS: MetricInfo = {
  label: "Desemprego baixo",
  description: "O desemprego abaixo da história aquece os salários e puxa a inflação",
  definition:
    "A curva de Phillips: com menos gente procurando emprego, as empresas pagam mais para contratar e repassam aos preços. Cada ponto de desemprego abaixo da história soma 0,35 ponto ao IPCA de 12 meses; acima da história, tira.",
  example: "Ex.: desemprego de 7,4% contra 9,4% na história (2 pontos abaixo) soma 0,7 ponto ao IPCA.",
  reading:
    "O número é o desemprego da partida menos o da história. Negativo empurra a inflação para cima, e o Banco Central sobe a SELIC 1,5 vez o tanto.",
  format: gapPoints,
};

export const FISCAL_RISK: MetricInfo = {
  label: "Risco fiscal",
  description: "O prêmio de risco da dívida acima da história",
  definition:
    "Quando a dívida cresce, quem empresta ao governo cobra um prêmio a mais. O real perde valor e os importados encarecem: cada ponto de prêmio acima da história soma meio ponto ao IPCA, encarece o crédito na mesma medida e pesa na bolsa como um ponto de SELIC.",
  example:
    "Ex.: prêmio de 3 pontos contra 1 na história (2 a mais) soma 1 ponto ao IPCA e tira uns 5,8% da bolsa no trimestre.",
  reading:
    "Zero é a dívida igual à da história. Quanto maior, mais caro o governo se financia, e o juro faz a dívida crescer ainda mais: o prêmio não tem teto.",
  format: gapPoints,
};

export const GDP_GAP: MetricInfo = {
  label: "PIB acima da história",
  description: "O tamanho da economia contra o da história",
  definition:
    "O quanto o PIB da partida está maior (ou menor) que o da história, somando o crescimento a mais de cada mês. Empresa que vende mais vale mais: cada 1% de PIB acima da história levanta a bolsa em 2,5%, e a arrecadação acompanha o PIB.",
  example: "Ex.: um ano crescendo 1 ponto acima da história deixa o PIB 1% maior e a bolsa uns 2,5% mais alta.",
  reading: "Positivo levanta a bolsa e a arrecadação; negativo derruba as duas.",
  format: (value) => `${signedPoints(Number(value))}%`,
};

export const DEBT_RATE: MetricInfo = {
  label: "Taxa média da dívida",
  description: "O juro que a dívida inteira paga, ao ano",
  definition:
    "Parte da dívida (45%) segue a SELIC do dia; o resto paga o que os títulos travaram quando foram emitidos, na média dos últimos 36 meses, com o prêmio de risco da época.",
  example:
    "Ex.: SELIC de 10% e títulos que travaram 12% na média dão 0,45 × 10% + 0,55 × 12% = 11,1% ao ano. Uma alta da SELIC chega em parte na hora e o resto ao longo de 3 anos.",
  reading:
    "Quanto maior, mais a dívida cresce sozinha. Acima do crescimento do PIB somado à inflação, ela só para de subir com o governo arrecadando mais do que gasta.",
  format: percent,
};

export const DEBT_CAUSES: MetricInfo = {
  label: "De onde veio a dívida",
  description: "A variação da dívida ÷ PIB nos últimos meses, por causa",
  definition:
    "A dívida em % do PIB muda por quatro causas: o juro a aumenta; o crescimento e a inflação a encolhem, porque aumentam o PIB que a divide; e o resultado primário (o que o governo arrecada menos o que gasta, sem os juros) a abate quando sobra e a aumenta quando falta. As quatro somam a variação inteira.",
  example:
    "Ex.: juro +8,0 pontos, crescimento −1,3, inflação −3,0 e déficit primário +1,5 dão +5,2 pontos: a dívida foi de 70% para 75,2% do PIB.",
  reading:
    "Pontos positivos fazem a dívida subir. Se o juro passa do que o crescimento e a inflação tiram, só um superávit primário segura a dívida.",
  format: (value) => signedPoints(Number(value)),
};

export const FISCAL_IMPULSE: MetricInfo = {
  label: "Impulso fiscal",
  description: "O empurrão no crescimento quando o governo passa a gastar mais ou cobrar menos",
  definition:
    "Quando o resultado primário piora em 12 meses (gasto que sobe ou imposto que cai), sobra mais dinheiro para as famílias e as empresas gastarem: cada ponto do PIB de piora soma meio ponto ao alvo do crescimento. Mantido o patamar por um ano, o empurrão acaba; o PIB fica mais alto, mas não cresce mais rápido.",
  example: "Ex.: cortar imposto em 1% do PIB soma 0,5 ponto ao alvo do crescimento durante um ano.",
  reading: "Positivo empurra o crescimento; negativo (o governo apertando as contas) freia.",
  format: gapPoints,
};
