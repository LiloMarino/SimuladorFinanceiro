import usePageLabel from "@/shared/hooks/usePageLabel";
import type { EconomyPanel } from "@/types";
import { EconomyChart } from "../components/economy-chart";
import { EconomyKpis } from "../components/economy-kpis";
import { EconomyError, EconomySkeleton } from "../components/economy-states";
import { EconomyTable } from "../components/economy-table";
import { useEconomyPanel } from "../hooks/queries/useEconomyPanel";

export default function EconomyPage() {
  usePageLabel("Economia");
  const { data: panel, error, refetch } = useEconomyPanel();

  if (!panel) {
    return error ? <EconomyError onRetry={() => void refetch()} /> : <EconomySkeleton />;
  }

  return <EconomyContent panel={panel} />;
}

function EconomyContent({ panel }: { panel: EconomyPanel }) {
  return (
    <div className="grid gap-5">
      <p className="-mt-1 text-[13px] text-muted-foreground">
        A SELIC, a inflação e o juro real ao longo da partida. Valem na história real e no futuro gerado.
      </p>
      <EconomyKpis panel={panel} />
      <EconomyChart panel={panel} />
      <EconomyTable panel={panel} />
    </div>
  );
}
