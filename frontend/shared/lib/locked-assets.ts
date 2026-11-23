import type { PortfolioState } from "@/types";

type LockedKind = PortfolioState["locked_assets"][number]["kind"];

/** Nome e saída curta de cada tipo de patrimônio travado, numa definição só: toda tela que nomeia o tipo lê daqui. */
const LOCKED_KINDS: Record<LockedKind, { label: string; exit: string; headline: string; distributionNote?: string }> = {
  FGTS: {
    label: "FGTS",
    exit: "só sai na demissão",
    headline: "Caixa e FGTS: o FGTS conta no patrimônio, mas só sai na demissão.",
  },
  COMPANY_CAPITAL: {
    label: "Capital da empresa",
    exit: "só sai vendendo",
    headline: "Caixa e capital da empresa: o capital conta no patrimônio, mas só vira caixa vendendo uma parte.",
  },
  PENSION: {
    label: "Previdência",
    exit: "só sai resgatando, com IR",
    headline: "Caixa e previdência: o saldo conta no patrimônio, mas só sai resgatando, com IR.",
  },
  WELFARE_SAVINGS: {
    label: "Pé-de-Meia",
    exit: "libera a cada 2 anos",
    headline: "Caixa e Pé-de-Meia: o saldo conta no patrimônio e libera a cada 2 anos.",
  },
  REAL_ESTATE: {
    label: "Imóveis",
    exit: "vender leva até 1 mês",
    headline: "Quase tudo em imóveis: o aluguel é a sua renda, e o valor deles conta no patrimônio.",
    distributionNote:
      "O aluguel cai no caixa todo mês e o valor dos imóveis acompanha o IVG-R. Comprar e vender fica na página Profissão.",
  },
};

/** O nome e a saída do patrimônio travado quando nenhum tipo está em mãos (o histórico guarda só o saldo somado). */
const GENERIC = { label: "Patrimônio travado", exit: "só sai pela regra da profissão" };

export const GENERIC_LOCKED_LABEL = GENERIC.label;

export const lockedLabel = (kind: LockedKind) => LOCKED_KINDS[kind].label;

/** Os tipos que o jogador tem agora, juntos num nome só ("FGTS", "Capital da empresa"). */
export function lockedLabels(portfolio: PortfolioState) {
  return joined(portfolio, "label");
}

/** A saída curta dos tipos que o jogador tem agora ("só sai na demissão"). */
export function lockedExits(portfolio: PortfolioState) {
  return joined(portfolio, "exit");
}

/** O tipo de maior saldo entre os patrimônios travados: é ele quem dá o texto da carteira; sem nenhum, nulo. */
function dominantKind(portfolio: PortfolioState) {
  const [largest] = [...portfolio.locked_assets].sort((a, b) => Number(b.value) - Number(a.value));
  return largest?.kind;
}

/** A frase da faixa de patrimônio de quem só tem caixa e patrimônio travado, pelo tipo de maior saldo. */
export function lockedHeadline(portfolio: PortfolioState) {
  const kind = dominantKind(portfolio);
  return kind ? LOCKED_KINDS[kind].headline : undefined;
}

/** O aviso da distribuição do patrimônio que o tipo de maior saldo traz, quando traz. */
export function lockedDistributionNote(portfolio: PortfolioState) {
  const kind = dominantKind(portfolio);
  return kind ? LOCKED_KINDS[kind].distributionNote : undefined;
}

function joined(portfolio: PortfolioState, field: "label" | "exit") {
  const kinds = portfolio.locked_assets.map((asset) => LOCKED_KINDS[asset.kind][field]);
  return kinds.length > 0 ? kinds.join(" + ") : GENERIC[field];
}
