import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";

/** Item de navegação (menu lateral, abas etc.) */

export interface NavItem {
  key: string;
  label: string;
  endpoint: string;
  icon: IconDefinition;
}

export type RedirectState = {
  from?: {
    pathname: string;
  };
};
