import { Card } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { formatPercent } from "@/shared/lib/utils/formatting";
import type { EconomicIndicators } from "@/types";

type EconomicIndicatorsCardProps = {
  loading: boolean;
  data: EconomicIndicators | null;
};

export function EconomicIndicatorsCard({ loading, data }: EconomicIndicatorsCardProps) {
  if (loading || !data) {
    return (
      <Card className="p-6 flex items-center justify-center h-32">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </Card>
    );
  }

  const indicators = [
    { label: "CDI", value: data.cdi },
    { label: "SELIC", value: data.selic },
    { label: "IPCA (12m)", value: data.ipca },
  ];

  return (
    <Card className="p-6">
      <h3 className="font-semibold mb-4">Indicadores Econômicos</h3>
      <div className="flex flex-wrap gap-4">
        {indicators.map((i) => (
          <div key={i.label} className="flex-1 min-w-[120px] border rounded p-4 text-center">
            <p className="text-gray-600 text-sm">{i.label}</p>
            <p className="font-bold">{formatPercent(i.value / 100)}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
