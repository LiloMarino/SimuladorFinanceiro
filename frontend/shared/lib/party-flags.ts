import type { VoterValue } from "@/types";

export const FLAGS_PER_PARTY = 3;

/** A ordem dos valores em toda a página: a mesma dos eixos do perfil. */
export const VOTER_VALUES: VoterValue[] = [
  "FREE_MARKET",
  "SOCIAL_JUSTICE",
  "STABILITY",
  "DEVELOPMENT",
  "SAVER_PROTECTION",
  "PUBLIC_SERVICE",
];

/** Rótulo, o que a bandeira defende e a cor dela; a cor é um token do tema. */
export const VALUE_INFO: Record<VoterValue, { label: string; short: string; description: string; color: string }> = {
  FREE_MARKET: {
    label: "Mercado livre",
    short: "Mercado livre",
    description: "Imposto baixo na bolsa e na renda fixa",
    color: "var(--info)",
  },
  SOCIAL_JUSTICE: {
    label: "Justiça social",
    short: "Justiça social",
    description: "Taxar o ganho de capital de quem investe",
    color: "var(--chart-6)",
  },
  STABILITY: { label: "Estabilidade", short: "Estabilidade", description: "Inflação na meta", color: "var(--success)" },
  DEVELOPMENT: {
    label: "Desenvolvimento",
    short: "Desenvolvimento",
    description: "Isentar setores que geram emprego",
    color: "var(--warning)",
  },
  SAVER_PROTECTION: {
    label: "Proteção ao poupador",
    short: "Poupador",
    description: "Renda fixa, LCI e LCA isentas",
    color: "var(--secret)",
  },
  PUBLIC_SERVICE: {
    label: "Serviço público",
    short: "Serviço público",
    description: "Reajuste do servidor",
    color: "var(--chart-7)",
  },
};

/** Mercado livre e Justiça social se excluem: escolher uma trava a outra. */
const EXCLUSIVE: Partial<Record<VoterValue, VoterValue>> = {
  FREE_MARKET: "SOCIAL_JUSTICE",
  SOCIAL_JUSTICE: "FREE_MARKET",
};

/** A bandeira que `value` exclui, se houver. */
function exclusiveOf(value: VoterValue): VoterValue | undefined {
  return EXCLUSIVE[value];
}

/** Por que a bandeira não pode entrar na escolha agora; nulo quando pode. */
export function lockReason(value: VoterValue, selected: VoterValue[]): string | null {
  if (selected.includes(value)) return null;
  const partner = exclusiveOf(value);
  if (partner && selected.includes(partner)) return `Exclui ${VALUE_INFO[partner].label}`;
  if (selected.length >= FLAGS_PER_PARTY) return "Já são 3: tire uma";
  return null;
}
