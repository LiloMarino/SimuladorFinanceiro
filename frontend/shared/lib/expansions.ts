import { Landmark, type LucideIcon } from "lucide-react";

export type ExpansionKey = "government";

type ExpansionInfo = {
  label: string;
  /** Uma frase: o que a expansão acrescenta à partida */
  description: string;
  highlights: string[];
  icon: LucideIcon;
  /** Classe do fundo do emblema; literal para o Tailwind enxergar */
  emblemClass: string;
  /** Classe do fundo da faixa do cartão: a cor da expansão escurecendo para o fim */
  bannerClass: string;
};

/** As expansões que o host liga nas regras; uma expansão nova é uma entrada nova aqui. */
export const EXPANSIONS: Record<ExpansionKey, ExpansionInfo> = {
  government: {
    label: "Governo & Política",
    description: "Os jogadores fundam partidos e disputam a eleição para presidente.",
    highlights: [
      "Partidos com bandeiras, fundador, filiados e contribuições",
      "Eleitorado em seis grupos, cada um com apoio e rejeição por partido; pesquisa mensal e 2º turno",
      "Mandato de 4 anos, com uma reeleição",
    ],
    icon: Landmark,
    emblemClass: "bg-expansion-government",
    bannerClass:
      "bg-[repeating-linear-gradient(135deg,rgb(255_255_255/0.07)_0_2px,transparent_2px_14px),linear-gradient(120deg,var(--expansion-government),var(--foreground))]",
  },
};
