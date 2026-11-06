import { useState } from "react";
import { ErrorState } from "@/shared/components/error-state";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { TreasuryPosition, TreasuryTitle } from "@/types";
import { BuyDialog } from "../components/buy-dialog";
import { CatalogCard } from "../components/catalog-card";
import { HoldingsCard } from "../components/holdings-card";
import { RateChartCard } from "../components/rate-chart-card";
import { RiskThermometer } from "../components/risk-thermometer";
import { SellDialog } from "../components/sell-dialog";
import { TreasuryHeader } from "../components/treasury-header";
import { TreasurySkeleton } from "../components/treasury-skeleton";
import { useTreasuryCatalog } from "../hooks/queries/useTreasuryCatalog";
import { useTreasuryHistory } from "../hooks/queries/useTreasuryHistory";
import { useTreasuryPositions } from "../hooks/queries/useTreasuryPositions";

export default function TreasuryPage() {
  usePageLabel("Tesouro");
  const catalog = useTreasuryCatalog();
  const history = useTreasuryHistory();
  const positions = useTreasuryPositions();
  const { data: simulation } = useSimulationState();
  const [buying, setBuying] = useState<TreasuryTitle | null>(null);
  const [selling, setSelling] = useState<TreasuryPosition | null>(null);

  const error = catalog.error ?? history.error ?? positions.error;
  if (error) {
    return (
      <ErrorState
        title="Não deu para carregar o Tesouro"
        description="A partida continua; tente de novo."
        error={error}
        onRetry={() => {
          void catalog.refetch();
          void history.refetch();
          void positions.refetch();
        }}
      />
    );
  }

  // Daqui para baixo catálogo, histórico, posições e data da partida chegam resolvidos
  if (!catalog.data || !history.data || !positions.data || !simulation?.current_date) return <TreasurySkeleton />;
  const today = simulation.current_date;
  const withGovernment = catalog.data.thermometer !== null;

  return (
    <div className="grid gap-5">
      <TreasuryHeader catalog={catalog.data} />
      <CatalogCard catalog={catalog.data} today={today} onInvest={setBuying} />
      <HoldingsCard positions={positions.data} onSell={setSelling} />

      {/* A taxa e a dívida */}
      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_420px]">
        <RateChartCard history={history.data} nextReview={catalog.data.next_review} withGovernment={withGovernment} />
        <RiskThermometer thermometer={catalog.data.thermometer} />
      </div>

      {buying && <BuyDialog title={buying} currentDate={today} onClose={() => setBuying(null)} />}
      {selling && <SellDialog position={selling} currentDate={today} onClose={() => setSelling(null)} />}
    </div>
  );
}
