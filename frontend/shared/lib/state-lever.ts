import type { StateLever } from "@/types";

/** As alavancas de uma estatal: o preço que ela segura mexe no IPCA (combustíveis, energia) ou no juro do crédito (banco). */
export const STATE_LEVERS = ["FUEL", "ENERGY", "BANK"] as const satisfies readonly StateLever[];

export const STATE_LEVER_LABEL: Record<StateLever, string> = {
  FUEL: "Combustíveis",
  ENERGY: "Energia",
  BANK: "Banco",
};
