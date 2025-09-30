import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";

export interface NavItem {
  key: string;
  label: string;
  endpoint: string;
  icon: IconDefinition;
}