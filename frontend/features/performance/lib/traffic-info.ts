import type { MetricInfo } from "@/shared/lib/metric-info";

const plain = (value: string | number) => String(value);

export const RATE_INFO: MetricInfo = {
  label: "Msg/s",
  description: "Mensagens por segundo agora.",
  definition:
    "Quantas mensagens desse evento saíram por segundo nos últimos segundos. Cada jogador inscrito recebe uma.",
  example: "10 msg/s a 10× com um jogador é uma mensagem por dia simulado; a 100× vira 100.",
  reading: "Com a partida pausada fica em “—”: nada está saindo agora. O acumulado ao lado continua.",
  format: plain,
};

export const VOLUME_INFO: MetricInfo = {
  label: "Volume",
  description: "Bytes por segundo agora.",
  definition: "Quanto o servidor manda desse evento por segundo, somando todos os jogadores.",
  example: "1 MB/s é o navegador lendo e redesenhando 1 MB de dados a cada segundo.",
  reading: "Até umas centenas de KB/s o navegador acompanha; na casa dos MB/s, a tela começa a travar.",
  format: plain,
};

export const SENDS_INFO: MetricInfo = {
  label: "Envios",
  description: "Quantas vezes o servidor mandou o evento.",
  definition:
    "Quantas vezes o servidor publicou o evento desde que as medições foram zeradas. Um envio vira uma mensagem para cada jogador inscrito.",
  example: "Com 3 jogadores na carteira, 1 envio de portfolio_update vira 3 mensagens.",
  reading: "Compare com os dias simulados: um evento por dia que mostra 10 envios por dia está saindo de mais.",
  format: plain,
};

export const UNHEARD_INFO: MetricInfo = {
  label: "Sem ninguém",
  description: "Envios que nenhum jogador recebeu.",
  definition:
    "Envios em que ninguém estava inscrito no evento, por exemplo o preço de uma ação sem ninguém na tela dela. O servidor montou a mensagem e ela não foi a lugar nenhum.",
  example: "120 · 3% com 4.330 na coluna Envios quer dizer que 120 dos 4.330 envios foram montados à toa.",
  reading:
    "Perto de 0% está bom. Um evento pesado com percentual alto é trabalho jogado fora, que pesa no tempo de cada dia.",
  format: plain,
};

export const TOTAL_INFO: MetricInfo = {
  label: "Total",
  description: "Bytes somados desde que zerou.",
  definition: "Tudo o que saiu desse evento desde que as medições foram zeradas, somando todos os jogadores.",
  example: "480 MB em 10 minutos de partida é perto de 800 KB por segundo.",
  reading: "É a coluna que diz qual evento mais pesa no navegador ao longo da partida.",
  format: plain,
};

export const TYPICAL_INFO: MetricInfo = {
  label: "Típico",
  description: "O tamanho da mensagem comum.",
  definition: "Mediana do tamanho: metade das mensagens é menor que ele, metade é maior.",
  example: "Típico de 118 KB quer dizer que a mensagem comum desse evento tem uns 118 KB.",
  reading:
    "Abaixo de 10 KB é leve. Acima de 100 KB, e saindo pelo menos uma vez por segundo, aparece em laranja: é a primeira suspeita de tela travando. Usa os últimos 1.000 envios.",
  format: plain,
};

export const SIZE_P95_INFO: MetricInfo = {
  label: "p95",
  description: "O tamanho que 95% das mensagens não passam.",
  definition: "p95: 95 de cada 100 mensagens cabem nesse tamanho; só as 5% maiores passam dele.",
  example: "Típico de 2 KB com p95 de 200 KB quer dizer que de vez em quando sai uma mensagem cem vezes maior.",
  reading: "Perto do típico é o normal: o tamanho quase não varia. Usa os últimos 1.000 envios.",
  format: plain,
};

export const QUEUE_INFO: MetricInfo = {
  label: "Atraso p95",
  description: "Quanto a mensagem espera para sair.",
  definition:
    "Tempo entre o servidor decidir enviar e a mensagem ser entregue à conexão do jogador. 95 de cada 100 mensagens saem nesse tempo ou menos.",
  example: "Atraso p95 de 800 ms quer dizer que o navegador vê o dia com quase 1 s de atraso.",
  reading:
    "Até umas dezenas de ms está ótimo. Na casa das centenas, o servidor não dá conta de entregar e a tela fica para trás da partida. Usa as últimas 1.000 mensagens.",
  format: plain,
};
