import { displayMoney, displayNumber, displayPercent } from "@/shared/lib/utils/display";

/** Texto de uma métrica: a descrição curta fica ao lado do número; o resto vai na dica. */
export interface MetricInfo {
  label: string;
  description: string;
  definition: string;
  example: string;
  reading: string;
  format: (value: string | number) => string;
}

const percent = (value: string | number) => displayPercent(value);
const ratio = (value: string | number) => displayNumber(String(value));

export const ANNUAL_RETURN: MetricInfo = {
  label: "Retorno anual",
  description: "Quanto a carteira rendeu, no ritmo de um ano",
  definition:
    "O retorno da cota (que só os rendimentos movem, sem contar aportes) composto para 252 dias úteis: quanto teria rendido se o ritmo do período durasse um ano inteiro.",
  example: "Ex.: +2% em 63 pregões (~3 meses) equivale a ~8,2% ao ano.",
  reading: "Compare com o CDI do mesmo período: abaixo dele, deixar o dinheiro num CDB teria rendido mais.",
  format: percent,
};

export const CUMULATIVE_RETURN: MetricInfo = {
  label: "Retorno acumulado",
  description: "Quanto a carteira rendeu desde o começo, sem contar aportes",
  definition:
    "A variação da cota desde o primeiro dia. O aporte mensal entra como capital, não como ganho, então só o que os investimentos renderam move a linha.",
  example: "Ex.: a cota foi de 1,00 para 1,15 → +15%, mesmo que o patrimônio tenha dobrado com aportes.",
  reading: "As linhas tracejadas são o CDI e o Ibovespa no mesmo período: acima delas, a carteira bateu a referência.",
  format: percent,
};

export const NETWORTH: MetricInfo = {
  label: "Patrimônio",
  description: "Caixa + investimentos de cada jogador, dia a dia, com os aportes",
  definition: "O patrimônio total no fim de cada dia útil: caixa, renda variável a preço de mercado e renda fixa.",
  example: "Ex.: R$ 10.000 iniciais com R$ 1.000 de aporte por mês sobem mesmo sem render nada.",
  reading: "Mostra o tamanho da carteira; para saber quem investiu melhor, olhe o retorno acumulado.",
  format: (value) => displayMoney(value),
};

export const CAPITAL_PROVIDED: MetricInfo = {
  label: "Capital aportado",
  description: "Saldo inicial + aportes",
  definition: "Todo o dinheiro que o jogador colocou na carteira: o saldo inicial e os aportes mensais até o último dia.",
  example: "Ex.: R$ 10.000 iniciais e 12 aportes de R$ 1.000 → R$ 22.000.",
  reading: "É a base do retorno em R$ e em %, que aparece na aba Geral.",
  format: (value) => displayMoney(value),
};

export const MONTHS_ABOVE_CDI: MetricInfo = {
  label: "Meses acima do CDI",
  description: "Em quantos meses a carteira rendeu mais que o CDI",
  definition: "Cada mês civil da partida conta como um mês; o retorno dele é comparado com o CDI acumulado no mesmo mês.",
  example: "Ex.: 9 de 12 → bateu o CDI em 75% dos meses.",
  reading: "Quanto mais, mais regular. Abaixo da metade, o CDI ganhou na maioria dos meses.",
  format: (value) => String(value),
};

export const POSITIVE_MONTHS: MetricInfo = {
  label: "Meses no positivo",
  description: "Em quantos meses a carteira subiu",
  definition: "Meses em que o retorno da cota foi maior que zero, sem contar o aporte.",
  example: "Ex.: 10 de 12 → só dois meses fecharam no vermelho.",
  reading: "Quanto mais, mais tranquilo o caminho.",
  format: (value) => String(value),
};

export const MAX_DRAWDOWN: MetricInfo = {
  label: "Queda máxima",
  description: "Maior queda do patrimônio a partir de um pico",
  definition:
    "Drawdown máximo: a maior queda a partir de um pico, antes de recuperá-lo. Aportes não contam como recuperação.",
  example: "Ex.: o patrimônio sobe a R$ 15.000 e cai a R$ 12.000 → 20%.",
  reading: "Quanto menor, melhor. Acima de ~30% é uma queda que a maioria das pessoas não aguenta sem vender.",
  format: percent,
};

export const DRAWDOWN: MetricInfo = {
  ...MAX_DRAWDOWN,
  label: "Distância do pico",
  description: "Quanto cada jogador está abaixo do próprio pico, dia a dia",
  definition:
    "A cada dia, quanto a cota está abaixo do maior valor que já alcançou. Zero é estar no topo; a linha só desce quando há queda.",
};

export const ANNUAL_VOLATILITY: MetricInfo = {
  label: "Volatilidade anual",
  description: "Quanto o patrimônio sobe e desce de um dia para o outro",
  definition:
    "Desvio-padrão dos retornos diários × √252 dias úteis: o tamanho típico da oscilação, em ritmo de um ano.",
  example: "Ex.: ~1% ao ano é renda fixa; ~25% é uma carteira só de ações.",
  reading: "Quanto menor, mais tranquilo o caminho. Não diz se o resultado foi bom, só o quanto balançou.",
  format: percent,
};

export const ROLLING_VOLATILITY: MetricInfo = {
  ...ANNUAL_VOLATILITY,
  label: "Volatilidade em janela móvel",
  description: "A volatilidade anual dos últimos 63 pregões (~3 meses), dia a dia",
  definition:
    "A cada dia, a volatilidade anual calculada só com os 63 pregões anteriores. Mostra os períodos agitados e os calmos, que a volatilidade do período inteiro mistura.",
};

export const SHARPE_RATIO: MetricInfo = {
  label: "Índice de Sharpe",
  description: "Retorno acima do CDI por unidade de oscilação",
  definition: "(retorno anual − CDI anual) ÷ volatilidade anual. Mede se o risco corrido foi pago.",
  example: "Ex.: retorno de 18%, CDI de 10%, volatilidade de 16% → 0,50.",
  reading: "Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro.",
  format: ratio,
};

export const SORTINO_RATIO: MetricInfo = {
  label: "Índice de Sortino",
  description: "Como o Sharpe, mas só a oscilação para baixo conta como risco",
  definition:
    "(retorno anual − CDI anual) ÷ oscilação dos dias que renderam menos que o CDI. Subir muito de uma vez não é punido.",
  example: "Ex.: 8 p.p. acima do CDI com oscilação de queda de 10% ao ano → 0,80.",
  reading: "Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro. Fica acima do Sharpe quando as oscilações são mais para cima.",
  format: ratio,
};

export const TIME_UNDERWATER: MetricInfo = {
  label: "Maior tempo abaixo do pico",
  description: "Quantos pregões seguidos o patrimônio levou para voltar ao topo",
  definition: "A maior sequência de dias úteis com a cota abaixo do pico anterior.",
  example: "Ex.: caiu em março e só voltou ao topo em setembro → ~126 pregões.",
  reading: "Quanto menor, melhor. 252 pregões é um ano inteiro no prejuízo em relação ao topo.",
  format: (value) => `${value} pregões`,
};

export const WORST_MONTH: MetricInfo = {
  label: "Pior mês",
  description: "O pior retorno mensal da partida",
  definition: "O menor retorno da cota entre os meses civis da partida, sem contar o aporte.",
  example: "Ex.: −5% → no pior mês, cada R$ 1.000 virou R$ 950.",
  reading: "Quanto mais perto de zero, melhor. Abaixo de −10% num mês é um tombo forte.",
  format: percent,
};

export const RISK_RETURN: MetricInfo = {
  label: "Risco × retorno",
  description: "Um ponto por jogador: quanto oscilou (para a direita) e quanto rendeu (para cima)",
  definition: "Eixo horizontal: volatilidade anual. Eixo vertical: retorno anual. Os dois do período inteiro.",
  example: "Ex.: um ponto em 10% de volatilidade e 15% de retorno rendeu mais com menos sobe-e-desce que um em 25% e 12%.",
  reading: "Quanto mais para cima e para a esquerda, melhor: mais retorno com menos risco.",
  format: percent,
};

export const SAMPLE_DAYS: MetricInfo = {
  label: "Amostra",
  description: "Quantos retornos diários entraram no cálculo",
  definition: "Número de dias úteis com retorno medido. Cada métrica de risco é calculada sobre essa amostra.",
  example: "Ex.: 63 pregões são ~3 meses; 252 pregões, um ano.",
  reading: "Com poucos pregões, as métricas mudam muito de um dia para o outro; abaixo de ~63, leia com cautela.",
  format: (value) => `${value} pregões`,
};

export const COMPOSITION: MetricInfo = {
  label: "Composição do patrimônio",
  description: "Caixa, renda variável e renda fixa empilhados, dia a dia",
  definition: "Quanto do patrimônio estava parado em caixa, em ações e em renda fixa a cada dia útil.",
  example: "Ex.: uma faixa de renda variável que engorda mostra o jogador entrando na bolsa.",
  reading: "Não há composição certa: mostra o estilo de cada jogador e quando ele mudou de ideia.",
  format: (value) => displayMoney(value),
};

export const SECTOR_EXPOSURE: MetricInfo = {
  label: "Exposição por setor",
  description: "Como a renda variável de cada jogador estava dividida entre os setores no último dia",
  definition:
    "A fração do valor em ações de cada setor, a preço do último dia. A classificação das ações se edita na Central de dados.",
  example: "Ex.: R$ 6.000 em bancos e R$ 4.000 em mineração → Financeiro 60%, Materiais Básicos 40%.",
  reading: "Compare as barras para ver quem apostou em quê; uma barra de uma cor só é uma aposta concentrada.",
  format: percent,
};

export const EFFECTIVE_SECTORS: MetricInfo = {
  label: "Número efetivo de setores",
  description: "Em quantos setores a renda variável está espalhada, na prática",
  definition: "1 ÷ soma dos quadrados das frações de cada setor. Pesa mais os setores grandes.",
  example: "Ex.: tudo num setor → 1; dividido igual em 4 → 4; 70/10/10/10 → ~1,9.",
  reading: "Quanto maior, mais diversificado. Abaixo de 2 é concentrado num setor só. Ações sem setor contam como um setor.",
  format: ratio,
};

export const SECTOR_PROFIT: MetricInfo = {
  label: "Lucro por setor",
  description: "De onde veio o resultado da renda variável",
  definition:
    "Por setor: o que entrou nas vendas, menos o que saiu nas compras, mais o valor do que ainda está na carteira no último dia. Antes do IR.",
  example: "Ex.: comprou R$ 3.000 de bancos, vendeu R$ 1.280 e ainda tem R$ 2.100 → +R$ 380.",
  reading: "Verde é setor que deu lucro; vermelho, prejuízo.",
  format: (value) => displayMoney(value),
};

export const MONTHLY_VOLUME: MetricInfo = {
  label: "Volume negociado por mês",
  description: "Quanto cada jogador comprou e vendeu em ações a cada mês",
  definition: "Soma de quantidade × preço de todas as compras e vendas executadas no mês.",
  example: "Ex.: comprar R$ 5.000 e vender R$ 3.000 num mês → R$ 8.000 negociados.",
  reading: "Mostra quando cada jogador esteve mais ativo; meses vazios são meses só segurando.",
  format: (value) => displayMoney(value),
};

export const BUY_TRADES: MetricInfo = {
  label: "Compras",
  description: "Negócios de compra executados",
  definition: "Cada execução conta uma vez: uma ordem preenchida em partes conta como vários negócios.",
  example: "Ex.: uma ordem de 1.000 ações preenchida em 3 partes → 3 compras.",
  reading: "Junto com as vendas, mostra o quanto o jogador operou.",
  format: (value) => String(value),
};

export const SELL_TRADES: MetricInfo = {
  ...BUY_TRADES,
  label: "Vendas",
  description: "Negócios de venda executados",
  example: "Ex.: vender uma posição de uma vez → 1 venda.",
};

export const TRADED_VOLUME: MetricInfo = {
  ...MONTHLY_VOLUME,
  label: "Volume negociado",
  description: "Compras + vendas da partida inteira, em R$",
};

export const TURNOVER: MetricInfo = {
  label: "Giro",
  description: "Quantas vezes a carteira foi negociada no período",
  definition: "Volume negociado (compras + vendas) ÷ patrimônio médio do período.",
  example: "Ex.: patrimônio médio de R$ 100 mil e R$ 300 mil negociados → 3,00.",
  reading: "Não é bom nem ruim sozinho: giro alto é estratégia ativa, e cada venda com lucro paga IR.",
  format: ratio,
};

export const INCOME_TAX_PAID: MetricInfo = {
  label: "IR pago",
  description: "Imposto sobre o lucro das vendas que já saiu do caixa",
  definition: "Soma dos DARFs da renda variável pagos na partida: 15% sobre lucro de ações (isento até R$ 20 mil de vendas no mês), 20% em FII e day trade.",
  example: "Ex.: R$ 5.000 de lucro vendendo R$ 30.000 em ações num mês → R$ 750 no mês seguinte.",
  reading: "Já está descontado do patrimônio e do retorno.",
  format: (value) => displayMoney(value),
};

export const IMPACT_COST: MetricInfo = {
  label: "Custo de impacto",
  description: "Quanto as ordens grandes mexeram no preço contra o jogador",
  definition:
    "Em cada negócio, preço executado − preço histórico do dia: comprar acima e vender abaixo do histórico é custo; o contrário é ganho. Só existe com o impacto de preço ligado.",
  example: "Ex.: comprar 100 ações a R$ 11 com o histórico em R$ 10 → R$ 100 de custo.",
  reading: "Positivo é custo; negativo, o impacto (das ordens de todos) jogou a favor.",
  format: (value) => displayMoney(value),
};

/** Valor formatado, ou "—" enquanto a série ainda não permite medir. */
export function displayMetric(metric: MetricInfo, value: string | number | null | undefined) {
  return value === null || value === undefined ? "—" : metric.format(value);
}
