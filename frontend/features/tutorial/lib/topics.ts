import type { ComponentType } from "react";
import { TrendingUp } from "lucide-react";
import { TOPIC_IDS, type TopicId } from "@/shared/lib/tutorial-topic-ids";

/** Parte da linha do tempo da animação: a partir de `start` (s) vale o passo `step` do texto. */
export interface Beat {
  start: number;
  step: number;
}

export interface IllustrationProps {
  /** Índice do trecho em cena na linha do tempo do tópico. */
  beat: number;
  /** Passo do texto a que o trecho pertence, a partir de 0. */
  step: number;
  /** Imagem parada: sem cursor, marcador nem digitação. */
  still?: boolean;
}

type TopicBase = {
  id: TopicId;
  group: keyof typeof groups;
  title: string;
  /** Duração de leitura, em minutos. */
  minutes: number;
  summary: string;
  /** Rotas (padrão do react-router) em que o aviso oferece este tópico. */
  screens: readonly string[];
  /** A ilustração vive num chunk à parte, que leva o `motion`. */
  loadIllustration: () => Promise<{ default: ComponentType<IllustrationProps> }>;
};

export type HowToTopic = TopicBase & {
  kind: "howto";
  /** Frase de abertura, acima dos passos. */
  intro: string;
  /** Passos do texto; `**trecho**` vira negrito. */
  steps: readonly string[];
  tip: string;
  beats: readonly Beat[];
  /** Duração do loop, em segundos, sem a pausa de recomeço. */
  duration: number;
  /** Trecho que fica na tela quando a animação falha. */
  poster: number;
};

export type ConceptTopic = TopicBase & {
  kind: "concept";
  body: string;
  callout: { title: string; text: string };
};

export type Topic = HowToTopic | ConceptTopic;

export const groups = {
  "variable-income": { label: "Renda variável", icon: TrendingUp },
} as const;

// Um tópico por id de TOPIC_IDS, e a chave é o id do próprio tópico
const registry = {
  "buy-stock": {
    id: "buy-stock",
    group: "variable-income",
    kind: "howto",
    title: "Comprar uma ação",
    minutes: 1,
    summary: "Escolher a ação, comprar pela boleta e achar ela na carteira.",
    intro: "Comprar é trocar caixa por ações. Se o preço sobe, a ação passa a valer mais que o que você pagou.",
    screens: ["/variable-income"],
    steps: [
      "Abra **Renda variável** e escolha a ação na lista.",
      "Clique em **Comprar** e diga quantas ações quer.",
      "Antes de confirmar, a boleta mostra o **total** e quanto sobra de **caixa**.",
      "Confirmou: a ação vai para a **Carteira**, pelo preço do dia na partida.",
    ],
    tip: "Com impacto de preço ligado na sala, comprar muito de uma vez sai um pouco mais caro: a boleta já mostra o preço final.",
    duration: 13,
    beats: [
      { start: 0, step: 0 },
      { start: 1, step: 0 },
      { start: 2, step: 0 },
      { start: 4, step: 1 },
      { start: 5, step: 1 },
      { start: 6, step: 2 },
      { start: 9, step: 3 },
      { start: 10, step: 3 },
      { start: 11, step: 3 },
    ],
    poster: 6,
    loadIllustration: () => import("../topics/buy-stock"),
  },
  "order-types": {
    id: "order-types",
    group: "variable-income",
    kind: "howto",
    title: "Ordem a mercado e limitada",
    minutes: 1,
    summary: "Comprar na hora pelo melhor preço, ou esperar o preço que você quer.",
    intro: "Toda compra entra no mercado como uma ordem: você escolhe entre comprar já ou esperar o preço que quer.",
    screens: ["/variable-income/:ticker"],
    steps: [
      "Toda compra é uma ordem. Na boleta você escolhe entre **A mercado** e **Limitada**.",
      "**A mercado** compra agora, pelo melhor preço de venda que existe no livro.",
      "Na **Limitada** você diz o preço máximo que aceita pagar.",
      "A ordem **espera** no livro até alguém vender a esse preço; quando o preço chega lá, ela executa.",
    ],
    tip: "A ordem limitada que ainda não executou fica no livro da sala, e você pode cancelá-la enquanto espera.",
    duration: 14,
    beats: [
      { start: 0, step: 0 },
      { start: 2, step: 1 },
      { start: 3.5, step: 1 },
      { start: 5, step: 2 },
      { start: 5.8, step: 2 },
      { start: 7, step: 3 },
      { start: 10, step: 3 },
      { start: 12, step: 3 },
    ],
    poster: 5,
    loadIllustration: () => import("../topics/order-types"),
  },
  leverage: {
    id: "leverage",
    group: "variable-income",
    kind: "concept",
    title: "Alavancagem",
    minutes: 2,
    summary: "Investir com dinheiro emprestado: o ganho e a perda crescem juntos.",
    screens: ["/credit"],
    body: "Alavancagem é a **dívida dividida pelo seu patrimônio** (o que você tem menos o que deve). Com R$ 10.000 seus e R$ 10.000 emprestados, a dívida é igual ao patrimônio: **100%**. Com o dobro investido, o ganho e a perda também dobram.",
    callout: {
      title: "Bom e ruim",
      text: "Sem dívida é 0%, o melhor. Cada 10% tira 4 dos 40 pontos que a alavancagem vale na nota de risco: em 25% você perde 10 pontos, e em 100% perde os 40. Acima de 100%, você deve mais do que tem.",
    },
    loadIllustration: () => import("../topics/leverage"),
  },
} as const satisfies { [K in TopicId]: Topic & { id: K } };

export type RegisteredTopic = (typeof registry)[TopicId];

export const topicList: readonly RegisteredTopic[] = TOPIC_IDS.map((id) => registry[id]);

export const findTopic = (id: TopicId): RegisteredTopic => registry[id];

/** Grupos que têm mais de um tópico abrem e fecham; tópico sozinho aparece solto na lista. */
export function groupTopics(list: readonly RegisteredTopic[]) {
  const keys = [...new Set(list.map((topic) => topic.group))];
  return keys.map((key) => ({ key, topics: list.filter((topic) => topic.group === key) }));
}
