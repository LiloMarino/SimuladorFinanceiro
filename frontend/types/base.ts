import type { LucideIcon } from "lucide-react";

/** Item de navegação (menu lateral, abas etc.) */

export interface NavItem {
  key: string;
  label: string;
  endpoint: string;
  icon: LucideIcon;
  group: "Mercado" | "Você" | "Ferramentas";
  badge?: string;
  /** `warning`: selo âmbar (ferramentas de debug) */
  badgeTone?: "warning";
  /** Só aparece com o modo debug ligado e para o host */
  debugOnly?: boolean;
}

export type RedirectState = {
  from?: {
    pathname: string;
  };
};
