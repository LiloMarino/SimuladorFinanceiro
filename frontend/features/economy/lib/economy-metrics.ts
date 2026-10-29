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
    "Uma média do preço das maiores ações da bolsa, em pontos. Sobe quando a bolsa em geral sobe e cai quando ela cai. Aqui ele já conta o efeito das medidas de gasto: a SELIC mais alta tira 2,9% da bolsa por ponto, no trimestre.",
  example: "Ex.: de 78.800 para 75.700 pontos é uma queda de 3,9%: uma carteira que acompanha a bolsa perde 3,9%.",
  reading:
    "Mais alto é bom para quem tem ações. Compare com a história ao lado: a diferença é o que as medidas do governo fizeram.",
  format: (value) => Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 0 }),
};

export const EFFECT_IPCA = {
  definition:
    "Quantos pontos a medida soma hoje ao IPCA de 12 meses. O efeito chega meses depois de a medida valer, fica cheio e cai pela metade a cada 12 meses.",
  example: "Ex.: +0,55 com o IPCA da história em 2,40% leva a inflação da partida a 2,95%.",
  reading:
    "Vermelho é inflação a mais; verde, a menos. Zero ou traço quer dizer que o efeito ainda não chegou ou já sumiu.",
};

export const EFFECT_SELIC = {
  definition:
    "O quanto o Banco Central sobe (ou corta) a SELIC por causa da inflação que a medida soma: 1,5 vez o tanto.",
  example: "Ex.: +0,55 ponto de inflação leva a +0,83 ponto de SELIC (0,55 × 1,5).",
  reading: "SELIC mais alta encarece o crédito e faz a renda fixa render mais; menos crescimento no curto prazo.",
};

export const EFFECT_STOCKS = {
  definition:
    "Quanto a bolsa anda no trimestre por causa da SELIC que a medida move: cada ponto de SELIC a mais tira 2,9% da bolsa, e ações de beta alto (que se mexem mais que o Ibovespa) sentem mais.",
  example: "Ex.: +0,83 ponto de SELIC tira uns 2,4% do Ibovespa no trimestre.",
  reading: "Negativo, a bolsa cai por causa da medida; positivo, sobe. Vale para toda ação, ajustada pelo beta dela.",
};
