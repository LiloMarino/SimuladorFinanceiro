import { useState, type ReactNode } from "react";
import { PageLabelContext } from "./PageLabelContext";

interface PageLabelProviderProps {
  children: ReactNode;
  routeLabels?: Record<string, string>;
}

export function PageLabelProvider({ children, routeLabels }: PageLabelProviderProps) {
  const [label, setLabel] = useState<string>("Untitled");

  return <PageLabelContext.Provider value={{ label, setLabel, routeLabels }}>{children}</PageLabelContext.Provider>;
}
