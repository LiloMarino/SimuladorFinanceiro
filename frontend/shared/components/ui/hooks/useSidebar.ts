import * as React from "react";
import { SidebarContext } from "../context/SidebarContext";

export function useSidebar() {
  const ctx = React.useContext(SidebarContext);
  if (!ctx) {
    throw new Error("useSidebar deve ser usado dentro de <SidebarProvider>");
  }
  return ctx;
}
