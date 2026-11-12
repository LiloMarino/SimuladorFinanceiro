import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { EconomyPanel } from "@/types";
import { DebtCard } from "../components/debt-card";
import { DollarCard } from "../components/dollar-card";
import { EconomyChart } from "../components/economy-chart";
import { EffectsCard } from "../components/effects-card";
import { EconomyKpis } from "../components/economy-kpis";
import { GrowthCard } from "../components/growth-card";
import { UnemploymentCard } from "../components/unemployment-card";
import { useEconomyPanel } from "@/shared/hooks/queries/useEconomyPanel";

export default function EconomyPage() {
  usePageLabel("Economia");
  const { data: panel, error, refetch } = useEconomyPanel();

  if (!panel) {
    return (
      <CardState
        bare
        label="Carregando a economia"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar a economia"
      >
        <Skeleton className="h-28" />
        <Skeleton className="h-96" />
        <div className="grid gap-5 lg:grid-cols-2">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </CardState>
    );
  }

  return <EconomyContent panel={panel} />;
}

function EconomyContent({ panel }: { panel: EconomyPanel }) {
  return (
    <div className="grid gap-5">
      <p className="-mt-1 text-[13px] text-muted-foreground">
        Os números da economia ao longo da partida. Valem na história real e no futuro gerado: o PIB e o desemprego são
        as séries do IBGE, mais o que o governo muda.
      </p>
      <EconomyKpis panel={panel} />
      <EconomyChart panel={panel} />
      {panel.effects && panel.links && <EffectsCard panel={panel} effects={panel.effects} links={panel.links} />}
      <div className="grid items-start gap-5 lg:grid-cols-2">
        <GrowthCard panel={panel} />
        <UnemploymentCard panel={panel} />
        <DollarCard panel={panel} />
      </div>
      {panel.debt && <DebtCard panel={panel} debt={panel.debt} />}
    </div>
  );
}
