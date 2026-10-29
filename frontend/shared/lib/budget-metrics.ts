import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayPercent } from "@/shared/lib/utils/display";

const percent = (value: string | number) => displayPercent(value, 1);

/** Pontos percentuais por extenso; até 2 o português fica no singular ("1,9 ponto", "2,45 pontos"). */
export function displayPoints(points: number, digits: number) {
  const text = points.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  return `${text} ${Math.abs(points) < 2 ? "ponto" : "pontos"}`;
}

/** O prêmio chega em fração (0.0164) e é lido em pontos: "1,64 ponto". */
export function displayPremiumPoints(value: string | number) {
  return displayPoints(Number(value) * 100, 2);
}

export const GROWTH: MetricInfo = {
  label: "Crescimento do PIB",
  description: "Quanto a economia cresceu em 12 meses",
  definition:
    "O PIB é tudo o que o país produz num ano. O crescimento mostra quanto esse total aumentou em relação a 12 meses atrás.",
  example:
    "Ex.: 2% de crescimento quer dizer que o país produz 2% a mais do que há um ano: um PIB de R$ 7 tri vira R$ 7,14 tri.",
  reading:
    "Perto de 2% é o ritmo normal; acima de 3% a economia está aquecida e o governo ganha aprovação; abaixo de 0% é recessão e o desemprego sobe. Juro real alto e bolsa em queda esfriam o crescimento.",
  format: percent,
};

export const UNEMPLOYMENT: MetricInfo = {
  label: "Desemprego",
  description: "Quem procura trabalho e não acha",
  definition: "A parcela das pessoas que querem trabalhar e estão sem emprego.",
  example: "Ex.: 10% de desemprego quer dizer que, de cada 100 pessoas que querem trabalhar, 10 estão sem vaga.",
  reading:
    "Até uns 8% é um bom nível; acima de 12% é ruim e pesa na aprovação do governo, sobretudo entre quem depende de auxílio e de carteira assinada. Cai quando a economia cresce mais que 2% ao ano e sobe quando cresce menos.",
  format: percent,
};

export const DEBT_GDP: MetricInfo = {
  label: "Dívida ÷ PIB",
  description: "Quanto o governo deve perto do que o país produz num ano",
  definition: "A dívida pública dividida pelo PIB: o peso da dívida em relação ao tamanho da economia.",
  example:
    "Ex.: dívida de R$ 5 tri num país com PIB de R$ 10 tri dá 50%: o governo deve o equivalente à metade do que o país produz num ano.",
  reading:
    "Até 50% é confortável e os títulos novos do Tesouro não cobram prêmio; entre 50% e 80% o prêmio começa a pesar; acima de 90% ele dispara e a aprovação do governo sofre. A dívida cresce com o déficit e com os juros, e encolhe quando a economia cresce.",
  format: percent,
};

export const RISK_PREMIUM: MetricInfo = {
  label: "Prêmio de risco",
  description: "O juro extra que o Tesouro paga por dever muito",
  definition:
    "Quando a dívida passa de 50% do PIB, quem empresta ao governo cobra um juro a mais para se sentir seguro. Esse adicional, medido em pontos percentuais ao ano, vale para os títulos novos do Tesouro.",
  example:
    "Ex.: com prêmio de 1 ponto, um título que pagaria 10% ao ano passa a pagar 11%. Dívida de 80% do PIB cobra 1,64 ponto; de 90%, 2,45 pontos.",
  reading:
    "Zero com dívida até 50% do PIB e cada vez maior acima disso. Quem compra Tesouro ganha mais; o governo paga mais juros e perde aprovação.",
  format: displayPremiumPoints,
};
