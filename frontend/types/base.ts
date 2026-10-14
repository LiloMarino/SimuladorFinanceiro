import type { LucideIcon } from "lucide-react";

/** Item de navegação (menu lateral, abas etc.) */

export interface NavItem {
  key: string;
  label: string;
  endpoint: string;
  icon: LucideIcon;
  group: "Mercado" | "Você" | "Ferramentas";
  badge?: string;
}

export type RedirectState = {
  from?: {
    pathname: string;
  };
};
