import type { DividendPolicy, StateCompanySize } from "@/types";

export const SIZE_LABEL: Record<StateCompanySize, string> = {
  SMALL: "Pequena",
  MEDIUM: "Média",
  LARGE: "Grande",
};

export const sizeLabel = (size: StateCompanySize) => SIZE_LABEL[size].toLowerCase();

export const POLICY_LABEL: Record<DividendPolicy, string> = {
  REINVEST: "Reinvestir",
  NORMAL: "Normal",
  SQUEEZE: "Espremer",
};
