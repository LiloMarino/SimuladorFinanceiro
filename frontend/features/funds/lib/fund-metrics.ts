import type { MetricInfo } from "@/shared/lib/metric-info";

export const NET_WORTH: MetricInfo = {
  label: "Patrimônio",
  description: "Tudo que a gestora tem: caixa, ações e renda fixa, a preço de hoje",
  definition:
    "É a soma do caixa e do valor de mercado de tudo que a gestora carrega. É o dinheiro dos cotistas, somados: dividido pelas cotas, dá o patrimônio por cota.",
  example: "Ex.: R$ 40.000 em caixa + R$ 100.000 em ações + R$ 60.000 em renda fixa = patrimônio de R$ 200.000.",
  reading:
    "Maior patrimônio é uma gestora maior, com mais taxa de administração para o gestor. O que importa para o cotista não é o tamanho, e sim o patrimônio por cota.",
  format: (value) => `${value}`,
};

export const NAV_PER_QUOTA: MetricInfo = {
  label: "Patrimônio por cota",
  description: "O valor justo de uma cota, pelo que a gestora tem",
  definition:
    "É o patrimônio dividido pelo número de cotas. É quanto uma cota vale de verdade, pelas coisas que a gestora tem, e não pelo que alguém aceita pagar.",
  example: "Ex.: patrimônio de R$ 200.000 e 1.600 cotas: 200.000 ÷ 1.600 = R$ 125,00 por cota.",
  reading:
    "Subindo com o tempo, a gestora está rendendo para o cotista; caindo, está perdendo. Começa em R$ 100,00 e o que importa é a distância dali.",
  format: (value) => `${value}`,
};

export const MARKET_PRICE: MetricInfo = {
  label: "Preço no mercado",
  description: "O último preço a que a cota foi negociada",
  definition:
    "É o preço do último negócio da cota no livro de ofertas. Pode ficar acima ou abaixo do patrimônio por cota, conforme a procura.",
  example: "Ex.: a cota vale R$ 128,40 pelo patrimônio, mas alguém pagou R$ 141,20: é o preço no mercado.",
  reading:
    "Preço acima do patrimônio por cota é ágio: o mercado aposta no gestor. Abaixo é deságio: o mercado desconfia, ou há cotista com pressa de vender.",
  format: (value) => `${value}`,
};

export const RANKING_PRICE: MetricInfo = {
  label: "Preço de ranking",
  description: "O preço que vale na carteira e no ranking, difícil de manipular",
  definition:
    "É a média dos negócios dos últimos 20 pregões, pesada pelo tamanho de cada negócio e presa a 30% acima ou abaixo do patrimônio por cota. É o preço que conta quando a cota entra na carteira de alguém.",
  example:
    "Ex.: com patrimônio por cota de R$ 128,40, um negócio forçado a R$ 1.000 conta no máximo R$ 166,92 (128,40 × 1,30). Subir o preço no mercado não infla a carteira.",
  reading:
    "Perto do patrimônio por cota, é um preço honesto. Colado no teto de +30% ou no piso de -30%, o mercado está tentando pagar ou receber mais do que a gestora vale.",
  format: (value) => `${value}`,
};

export const PREMIUM: MetricInfo = {
  label: "Ágio",
  description: "Quanto o preço no mercado passa do patrimônio por cota",
  definition:
    "É o preço no mercado dividido pelo patrimônio por cota, menos 1. Positivo é ágio (a cota custa mais do que vale); negativo é deságio (custa menos).",
  example: "Ex.: R$ 141,20 ÷ R$ 128,40 − 1 = +10,0%. Quem compra paga R$ 12,80 a mais por cota do que ela vale.",
  reading:
    "Ágio é bom para o gestor, que vende cotas mais caras na oferta, e ruim para quem compra, que paga a mais. Deságio é o contrário. Perto de zero, o preço é justo.",
  format: (value) => `${value}%`,
};

export const RETURN_VS_CDI: MetricInfo = {
  label: "Rentabilidade em 12 meses",
  description: "Quanto a cota rendeu no ano, contra o CDI",
  definition:
    "É a variação do patrimônio por cota nos últimos 12 meses, ao lado do que o CDI, a taxa que os bancos pagam entre si, rendeu no mesmo período. O CDI é a régua da renda fixa segura.",
  example:
    "Ex.: a cota foi de R$ 100,00 a R$ 112,00: rendeu 12%. Com CDI de 10% no ano, rendeu 2 pontos a mais que o CDI.",
  reading:
    "Acima do CDI, o gestor entregou mais do que um investimento seguro e paga a taxa de performance. Abaixo, o cotista teria ganhado mais deixando o dinheiro parado em renda fixa.",
  format: (value) => `${value}%`,
};

export const MANAGEMENT_FEE: MetricInfo = {
  label: "Taxa de administração",
  description: "Uma parte do patrimônio que vai para o gestor todo mês, ganhe ou perca",
  definition:
    "Percentual ao ano sobre o patrimônio, cobrado em 12 parcelas e descontado da cota. Paga o trabalho de gerir, rendendo ou não.",
  example: "Ex.: R$ 100.000 de patrimônio a 1,5% ao ano: 100.000 × 1,5% ÷ 12 = R$ 125,00 por mês.",
  reading:
    "Taxa baixa atrai cotista; taxa alta come o rendimento. Até 1% ao ano é leve; acima de 2% pesa, a menos que o gestor entregue bem acima do CDI.",
  format: (value) => `${value}%`,
};

export const PERFORMANCE_FEE: MetricInfo = {
  label: "Taxa de performance",
  description: "Uma parte do que a cota render acima do CDI",
  definition:
    "Percentual cobrado só sobre o excesso: o quanto a cota rendeu a mais que o CDI, desde o último pico (a marca d'água). Sem excesso, não há cobrança.",
  example:
    "Ex.: cota de R$ 100,00 que vai a R$ 110,00 com CDI de 4% (R$ 104,00): excesso de R$ 6,00. A 20%, o gestor leva R$ 1,20 por cota.",
  reading:
    "Alinha o gestor com o cotista: ele só ganha se render mais que o CDI. Até 20% é o usual; acima disso fica caro para quem cota.",
  format: (value) => `${value}%`,
};

export const HIGH_WATER_MARK: MetricInfo = {
  label: "Marca d'água",
  description: "O maior valor que a cota já teve e já foi cobrado",
  definition:
    "É o pico do patrimônio por cota em que a taxa de performance foi cobrada pela última vez. Só se cobra de novo quando a cota passa dele, para o cotista não pagar duas vezes pelo mesmo ganho.",
  example:
    "Ex.: a marca é R$ 110,00. Se a cota cai a R$ 105,00 e volta a R$ 108,00, nada é cobrado; só o que passar de R$ 110,00 conta.",
  reading:
    "Marca d'água longe da cota de hoje: o gestor precisa recuperar a perda antes de voltar a receber performance. Colada na cota: está no pico.",
  format: (value) => `${value}`,
};

export const CONTROL: MetricInfo = {
  label: "Controle",
  description: "Ter mais da metade das cotas é ter a gestora nas mãos",
  definition:
    "É ter mais de 50% das cotas. Vender cotas ou emitir cotas novas numa oferta diminui a sua parte; abaixo de 50%, outro cotista pode passar à frente.",
  example: "Ex.: de 10.000 cotas, o controle exige 5.001. Com 5.800, o gestor pode vender 799 cotas e ainda controlar.",
  reading: "Acima de 50% a gestora é sua. Perto da marca, uma compra de outro cotista no mercado já a ameaça.",
  format: (value) => `${value}%`,
};
