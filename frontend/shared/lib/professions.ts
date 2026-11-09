import { Armchair, Briefcase, Building2, HandCoins, Landmark, Store, type LucideIcon } from "lucide-react";
import type { IncomeLoss, LifeStatus, Profession } from "@/types";

export type ProfessionInfo = {
  name: string;
  icon: LucideIcon;
  /** Renda do mês em múltiplos do salário que o host definiu */
  incomeMultiple: number;
  /** Quanto da renda vem do auxílio do governo, nos gastos de referência (o resto é a renda do trabalho) */
  benefitMultiple?: number;
  /** O que a renda sente: a medida do governo, o imposto e o sorteio de demissão */
  feels: string;
};

export const PROFESSIONS: Record<Profession, ProfessionInfo> = {
  CLT: {
    name: "CLT",
    icon: Briefcase,
    incomeMultiple: 1,
    feels:
      "Pode ser demitido quando o desemprego sobe. Reajuste: IPCA mais metade do crescimento do PIB. Sente o imposto de renda das pessoas.",
  },
  PUBLIC_SERVANT: {
    name: "Servidor",
    icon: Landmark,
    incomeMultiple: 0.9,
    feels:
      "Nunca é demitido. Reajuste: IPCA mais o aumento que o governo der aos servidores. Sente o imposto de renda das pessoas.",
  },
  ENTREPRENEUR: {
    name: "Empreendedor",
    icon: Store,
    incomeMultiple: 1.2,
    feels:
      "A renda sobe e desce com o PIB dos últimos 12 meses. Não é demitido. Sente o imposto de renda das empresas.",
  },
  RETIREE: {
    name: "Aposentado",
    icon: Armchair,
    incomeMultiple: 0.85,
    feels:
      "Nunca é demitido, mas o imprevisto de saúde custa o dobro. Reajuste: IPCA mais o aumento que o governo der aos aposentados.",
  },
  WELFARE: {
    name: "Auxílio",
    icon: HandCoins,
    incomeMultiple: 0.5,
    benefitMultiple: 0.4,
    feels:
      "Faz bico (perde a parte do bico no sorteio de demissão) e recebe o auxílio, que cresce com o gasto do governo. Sente o imposto sobre consumo.",
  },
  LANDLORD: {
    name: "Locador",
    icon: Building2,
    incomeMultiple: 1,
    feels:
      "Vive de aluguel: o sorteio de demissão vira vacância e o mês fica sem aluguel. Sente o imposto de renda das pessoas.",
  },
};

export const PROFESSION_ORDER = Object.keys(PROFESSIONS) as Profession[];

/** Renda de partida da profissão sobre o salário do host; o auxílio conta no gasto de referência. */
export function professionIncome(profession: Profession, salary: number) {
  const { incomeMultiple, benefitMultiple = 0 } = PROFESSIONS[profession];
  return salary * (incomeMultiple + benefitMultiple);
}

/** O que a demissão sorteada tira de cada profissão que a sente. */
export const INCOME_LOSS_NAMES: Record<IncomeLoss, { event: string; missing: string }> = {
  LAYOFF: { event: "Demitido", missing: "o salário" },
  GIG_LOSS: { event: "Bico perdido", missing: "a renda do bico" },
  VACANCY: { event: "Imóvel vago", missing: "o aluguel" },
};

/** O imposto cujo desvio contra a lei corta (ou soma à) a renda da profissão. */
export const TAX_NAMES: Record<NonNullable<LifeStatus["tax"]>, string> = {
  PERSONAL: "Imposto de renda das pessoas",
  CORPORATE: "Imposto de renda das empresas",
  CONSUMPTION: "Imposto sobre consumo",
};
