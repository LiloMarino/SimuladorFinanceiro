import { Card } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { InfoHint } from "@/shared/components/info-hint";
import { displayPercent } from "@/shared/lib/utils/display";
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
    {
      label: "CDI",
      value: data.cdi,
      hint: "Juro que os bancos cobram entre si por um dia, publicado pelo Banco Central. Aqui, o CDI do dia simulado levado para o ano (252 dias úteis). Ex.: 14,9% a.a. faz R$ 1.000 num CDB 100% do CDI virarem cerca de R$ 1.149 em um ano, se a taxa não mudar.",
    },
    {
      label: "SELIC",
      value: data.selic,
      hint: "Taxa básica de juros do Banco Central, o indexador do Tesouro Selic. Aqui, a taxa do dia simulado levada para o ano. Fica sempre muito perto do CDI.",
    },
    {
      label: "IPCA (12m)",
      value: data.ipca,
      hint: "Inflação oficial: quanto os preços subiram nos 12 meses até o mês simulado. Ex.: 4,5% quer dizer que o que custava R$ 100 passou a custar R$ 104,50. Investimento que rende menos que isso perde poder de compra.",
    },
  ];

  return (
    <Card className="p-6">
      <h3 className="font-semibold mb-4">Indicadores Econômicos</h3>
      <div className="flex flex-wrap gap-4">
        {indicators.map((i) => (
          <div key={i.label} className="flex-1 min-w-[120px] border rounded p-4 text-center">
            <div className="flex items-center justify-center gap-1">
              <p className="text-gray-600 text-sm">{i.label}</p>
              <InfoHint label={`O que é ${i.label}`}>{i.hint}</InfoHint>
            </div>
            <p className="font-bold">{displayPercent(i.value)}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
