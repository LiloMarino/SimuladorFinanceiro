import { createContext } from "react";

export interface PageLabelContextValue {
  label: string;
  setLabel: (label: string) => void;
  routeLabels?: Record<string, string>;
}

export const PageLabelContext = createContext<PageLabelContextValue | undefined>(undefined);
