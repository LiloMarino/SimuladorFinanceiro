import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";

export const MARK_TO_MARKET: MetricInfo = {
  label: "Marcação",
  description: "Quanto o preço de hoje está acima ou abaixo da curva do título",
  definition:
    "O Tesouro compra de volta pelo preço do dia, e esse preço sobe quando a taxa cai e desce quando a taxa sobe. A marcação é a diferença entre esse preço e o valor que o título teria seguindo a taxa que você travou na compra.",
  example:
    "Ex.: você comprou a 11,80% ao ano e hoje o mesmo título paga 13,52%. Quem compra agora ganha mais que você, então o seu vale menos: se pela curva ele valeria R$ 26.682,67 e o mercado paga R$ 24.266,25, a marcação é −R$ 2.416,42.",
  reading:
    "Positiva (verde) quando a taxa caiu desde a sua compra: vender antes do vencimento rende mais que a curva. Negativa (vermelha) quando a taxa subiu: vender agora perde parte do ganho. Esperar até o vencimento zera a marcação. O Tesouro Selic quase não marca, porque acompanha a taxa do dia.",
  format: (value) => {
    const amount = Number(value);
    return `${amount < 0 ? "−" : amount > 0 ? "+" : ""}${displayMoney(Math.abs(amount))}`;
  },
};

export const EQUIVALENT_TODAY: MetricInfo = {
  label: "Equivale hoje",
  description: "A taxa ao ano que o título rende, para comparar com os outros",
  definition:
    "Converte a taxa do título (um percentual do CDI, SELIC + algo ou IPCA + algo) em uma taxa fixa ao ano, usando os indicadores de hoje. Assim dá para pôr Selic, Prefixado e IPCA+ na mesma régua.",
  example:
    "Ex.: no IPCA+ soma o IPCA dos últimos 12 meses: IPCA + 9,45% com o IPCA a 4,60% equivale a 14,48%. O Prefixado já é uma taxa ao ano: 12,92% equivale a 12,92%.",
  reading:
    "Quanto maior, mais o título rende por ano. Para Selic e IPCA+ é uma estimativa: se o indicador mudar, o rendimento muda junto; o Prefixado é a única taxa certa desde a compra.",
  format: (value) => displayPercent(value),
};

export const TODAY_RATE: MetricInfo = {
  label: "Taxa de hoje",
  description: "O que o título paga para quem compra neste mês",
  definition:
    "A taxa do título é a soma de duas partes: a taxa base, que segue os juros e a inflação, e o prêmio de risco do país. A taxa que vale é a do mês da compra, e fica travada para quem comprou.",
  example:
    "Ex.: um Prefixado com base 11,18% e prêmio de 2,34 pontos paga 13,52% ao ano. Quem compra no mês seguinte pega a taxa nova; o seu continua em 13,52%.",
  reading:
    "A barra mostra o quanto da taxa é base (cinza) e o quanto é prêmio (cor da faixa de risco). Prêmio grande quer dizer país arriscado: rende mais, mas o governo paga mais juros e perde aprovação.",
  format: (value) => displayPercent(value),
};

export const SOLD_UNTIL: MetricInfo = {
  label: "À venda até",
  description: "Quando o título sai da vitrine e quem entra no lugar",
  definition:
    "Cada título tem um vencimento fixo, e o prazo que falta vai encurtando. Quando falta menos que o piso do título, ele sai da vitrine no fechamento de dezembro e entra um título de prazo mais longo no lugar.",
  example:
    "Ex.: o Tesouro Prefixado 2037 fica à venda até dez 2032; em dezembro de 2032 ele sai e entra um Prefixado de prazo mais longo.",
  reading:
    "Quem já comprou fica com o título até o vencimento ou vende antes pelo preço do dia. A saída da vitrine só impede compras novas.",
  format: (value) => String(value),
};

export const YIELDED: MetricInfo = {
  label: "Rendeu",
  description: "Quanto o título rendeu desde a compra, seguindo a taxa que você travou",
  definition:
    "O ganho que a curva do título acumulou sobre o que você aplicou, antes do imposto e sem a marcação a mercado. É o que você teria se o título valesse sempre o preço da curva.",
  example:
    "Ex.: você aplicou R$ 20.000 a 11,80% ao ano e hoje a curva diz que o título vale R$ 26.682,67: ele rendeu +R$ 6.682,67.",
  reading:
    "Sempre sobe com o tempo, porque os juros se acumulam dia a dia. Quanto vale a venda hoje depende também da marcação e do imposto de renda sobre o ganho.",
  format: (value) => displayMoney(value),
};
