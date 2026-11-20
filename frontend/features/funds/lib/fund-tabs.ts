import type { Comanager } from "./fund-comanagers";

/** Os diálogos da página: um aberto por vez, e qualquer aba pede o que precisa. */
export type FundDialog =
  | "invite"
  | "fees"
  | "distribution"
  | "offer"
  | "issuance"
  | "directed"
  | "buyback"
  | "contribute"
  | "merge";

const FUND_TABS = ["actions", "overview", "portfolio", "quotas", "income", "assembly", "report", "settings"] as const;
export type FundTab = (typeof FUND_TABS)[number];

/** O que as abas pedem à página: abrir um diálogo, trocar de aba ou mexer num co-gestor. */
export type FundTabActions = {
  open: (dialog: FundDialog) => void;
  goTo: (tab: FundTab) => void;
  changeShare: (comanager: Comanager) => void;
  remove: (comanager: Comanager) => void;
};

export const FUND_TAB_LABEL: Record<FundTab, string> = {
  actions: "Suas ações",
  overview: "Visão geral",
  portfolio: "Carteira",
  quotas: "Cotas",
  income: "Rendimentos",
  assembly: "Assembleia",
  report: "Relatório",
  settings: "Configurações",
};

// A carteira e as configurações são de quem gere; as outras abas são de qualquer cotista
const MANAGER_ONLY: readonly FundTab[] = ["portfolio", "settings"];

/** As abas que o jogador vê, na ordem da página. */
export const visibleTabs = (manager: boolean): FundTab[] =>
  FUND_TABS.filter((tab) => manager || !MANAGER_ONLY.includes(tab));

/** A aba vem do endereço (?tab=); sem ela ou com valor que o jogador não vê, abre Suas ações. */
export const tabFrom = (value: string | null, tabs: readonly FundTab[]): FundTab =>
  tabs.find((tab) => tab === value) ?? "actions";
