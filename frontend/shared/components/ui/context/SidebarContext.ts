import * as React from "react";

export interface SidebarContextValue {
  open: boolean;
  toggle: () => void;
}

export const SidebarContext = React.createContext<SidebarContextValue | null>(null);
