import BaseCard from "@/shared/components/base-card";
import { Badge } from "@/shared/components/ui/badge";
import type { FixedIncomeAsset } from "@/features/fixed-income/models/FixedIncomeAsset";

interface FixedIncomeCardProps {
  asset: FixedIncomeAsset;
}

export default function FixedIncomeCard({ asset }: FixedIncomeCardProps) {
  return (
    <BaseCard
      header={{
        title: asset.name,
        subtitle: (
          <>
            Emitido por: <span className="font-medium">{asset.issuer}</span>
          </>
        ),
        badge: (
          <Badge variant="outline" className="text-green-600 border-green-300 font-medium">
            {asset.rateLabel}
          </Badge>
        ),
      }}
      fields={[
        { label: "Vencimento:", value: asset.formattedMaturity },
        { label: "Índice:", value: asset.rateIndex },
        { label: "IR:", value: asset.incomeTaxLabel },
      ]}
      footer={{
        linkTo: asset.detailsLink,
        label: "Adicionar",
      }}
    />
  );
}
