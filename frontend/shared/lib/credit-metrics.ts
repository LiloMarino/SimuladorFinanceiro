import type { MetricInfo } from "@/shared/lib/metric-info";
import { displaySpread } from "@/shared/lib/credit";
import { displayPercent } from "@/shared/lib/utils/display";

export const LEVERAGE: MetricInfo = {
  label: "Alavancagem",
  description: "Quanto do patrimônio é dívida",
  definition: "A dívida dividida pelo patrimônio líquido (o que você tem menos o que deve).",
  example: "Ex.: R$ 100 mil de dívida com R$ 400 mil de patrimônio → 25%.",
  reading:
    "Sem dívida é 0%. Quanto menor, melhor: cada 10% tira 4 pontos da nota de risco, e acima de 100% você deve mais do que tem.",
  format: (value) => displayPercent(value, 1),
  topic: "leverage",
};

/** Alavancagem é dívida ÷ patrimônio: sem patrimônio positivo a razão não existe. */
export const displayLeverage = (value: string | null) => (value === null ? "sem patrimônio" : LEVERAGE.format(value));

export const VOLATILITY: MetricInfo = {
  label: "Volatilidade",
  description: "O quanto o patrimônio balança",
  definition:
    "O tamanho típico das oscilações diárias do patrimônio, levado para um ano. Mede o susto: uma carteira que sobe e desce muito é mais difícil de sustentar com parcela fixa.",
  example:
    "Ex.: 18% ao ano quer dizer que, num ano comum, o patrimônio costuma variar uns 18% para cima ou para baixo.",
  reading:
    "Quanto menor, melhor. De 0% a 45% ao ano a nota perde pontos aos poucos; 45% ou mais vale zero. Com menos de 21 pregões de histórico, vale como se fosse 0%.",
  format: (value) => displayPercent(value, 1),
};

export const LATE_PAYMENTS: MetricInfo = {
  label: "Pagamentos em dia",
  description: "Parcelas pagas no prazo",
  definition: "Conta as parcelas que foram pagas depois do vencimento nos últimos 12 meses.",
  example: "Ex.: 1 parcela atrasada tira 10 dos 30 pontos desta parte; 3 atrasos zeram os 30.",
  reading:
    "Quanto menos atrasos, melhor: sem nenhum, você mantém os 30 pontos. Parcela atrasada derruba a nota na hora e pesa por 12 meses.",
  format: (value) => String(value),
};

export const SPREAD: MetricInfo = {
  label: "Spread da nota",
  description: "O que o banco soma à SELIC para você",
  definition: "Pontos percentuais por ano acrescentados à SELIC. Quanto melhor a nota, menor o acréscimo.",
  example: "Ex.: nota A paga SELIC + 5. Com a SELIC em 4,25%, o juro é 4,25% + 5,00 = 9,25% ao ano.",
  reading: "Se a renda fixa mais cara do dia rende mais que isso, o juro sobe para essa taxa mais 0,5 ponto.",
  format: displaySpread,
};

export const PRICE_TABLE: MetricInfo = {
  label: "Tabela Price",
  description: "Parcela fixa, juro que cai a cada mês",
  definition:
    "O empréstimo é pago em parcelas de valor igual. No começo, a maior parte da parcela é juro; a cada mês o juro cai e a parte que abate a dívida cresce.",
  example: "Ex.: R$ 50.000 em 24 vezes a 9,25% ao ano → parcela de R$ 2.281,48 e R$ 4.755,40 de juro no total.",
  reading: "Pagar antes abate os juros que ainda não correram, então quitar cedo sai mais barato que seguir pagando.",
  format: (value) => String(value),
};

export const RISK_RATING: MetricInfo = {
  label: "Nota de risco",
  description: "Sua confiabilidade como devedor",
  definition:
    "Uma nota de 0 a 100 que vira uma letra, de AAA a D. Soma três partes: alavancagem (até 40 pontos), volatilidade (até 30) e pagamentos em dia (até 30).",
  example: "Ex.: 78 pontos é a nota A: juro de SELIC + 5 e dívida de até 60% do patrimônio.",
  reading:
    "Quanto mais alta, mais barato e mais amplo o crédito. Abaixo de 30 pontos é a nota D e não há empréstimo novo. A alavancagem e a volatilidade são recalculadas no fim do mês; parcela atrasada derruba a nota na hora.",
  format: (value) => `${value} de 100`,
};

export const COST_OF_DEBT: MetricInfo = {
  label: "Custo da dívida",
  description: "O juro médio que você paga",
  definition:
    "A média dos juros travados nos seus empréstimos, dando mais peso aos que ainda têm mais saldo a pagar. Sem dívida aberta, vale o juro dos contratos.",
  example: "Ex.: R$ 80 mil a 9,5% e R$ 20 mil a 12% → o custo médio fica perto de 10%, porque o maior saldo pesa mais.",
  reading:
    "Compare com o que a carteira rende: se ela rende mais que o custo da dívida, o empréstimo está trabalhando a seu favor; se rende menos, está comendo patrimônio.",
  format: (value) => `${displayPercent(value, 1)} a.a.`,
};

export const PAYROLL_MARGIN: MetricInfo = {
  label: "Margem consignável",
  description: "O máximo que as parcelas dos consignados podem somar por mês",
  definition:
    "35% do salário líquido. A parcela do consignado sai do salário antes de ele cair no caixa, e a soma de todas as parcelas não passa dessa margem.",
  example:
    "Ex.: salário líquido de R$ 4.850,00 → as parcelas somam até R$ 1.697,50 por mês. Com R$ 483,56 já usados, sobram R$ 1.213,94 para um novo contrato.",
  reading:
    "Livre alto: cabe outro consignado. Livre zero: só depois que um contrato terminar e a margem voltar a abrir.",
  format: (value) => displayPercent(value, 0),
};

export const LOCKED_RATE: MetricInfo = {
  label: "Juro travado no contrato",
  description: "A taxa que vale até a última parcela",
  definition:
    "A taxa do consignado é a SELIC do dia da assinatura mais 2 pontos ao ano. Ela fica fixa no contrato, mesmo que a SELIC mude depois.",
  example: "Ex.: assinado com a SELIC a 13,76% → 15,76% ao ano até o fim, mesmo que a SELIC suba para 18%.",
  reading:
    "Contratar com a SELIC baixa é bom: o juro fica baixo pelo prazo todo. Contratar com a SELIC alta trava um juro caro.",
  format: (value) => displayPercent(value, 2),
};
