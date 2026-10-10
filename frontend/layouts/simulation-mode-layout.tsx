import MainLayout from "@/layouts/main-layout";
import { PlainLayout } from "@/layouts/plain-layout";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { NavItem } from "@/types";

interface SimulationModeLayoutProps {
  navItems: NavItem[];
}

/** Tela que abre nos dois modos: com sidebar na partida, em tela cheia a partir do lobby. */
export function SimulationModeLayout({ navItems }: SimulationModeLayoutProps) {
  const { simulationActive } = useSimulation();
  return simulationActive ? <MainLayout navItems={navItems} /> : <PlainLayout />;
}
