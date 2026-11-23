import type { ProfessionMechanic } from "@/types";

type GraduateMechanic = Extract<ProfessionMechanic, { kind: "graduate" }>;

/** Uma linha da escada acadêmica, como o servidor entrega. */
export type GraduateStep = GraduateMechanic["steps"][number];

type StepText = {
  label: string;
  /** O nome com o artigo, em minúsculo: "a especialização" */
  withArticle: string;
  /** O nome com "em": "na especialização" */
  inside: string;
};

export const STEP_TEXTS: Record<GraduateStep["step"], StepText> = {
  GRADUATION: { label: "Graduação", withArticle: "a graduação", inside: "na graduação" },
  SPECIALIZATION: { label: "Especialização", withArticle: "a especialização", inside: "na especialização" },
  MASTERS: { label: "Mestrado", withArticle: "o mestrado", inside: "no mestrado" },
  DOCTORATE: { label: "Doutorado", withArticle: "o doutorado", inside: "no doutorado" },
};

/** A duração do degrau em anos cheios ou, quando não fecha o ano, em meses. */
export function displayStepDuration(months: number) {
  if (months % 12 !== 0) return `${months} meses`;
  const years = months / 12;
  return years === 1 ? "1 ano" : `${years} anos`;
}

/** O múltiplo do salário com uma casa: "1,6×". */
export function displayMultiple(value: string) {
  return `${new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(Number(value))}×`;
}
