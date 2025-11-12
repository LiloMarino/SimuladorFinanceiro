import BaseCard from "./base-card";
import { Badge } from "@/components/ui/badge";
import type { FixedIncomeAsset } from "@/models/fixed-income-asset";

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
        { label: "IR:", value: asset.incomeTax },
      ]}
      footer={{
        linkTo: asset.detailsLink,
        label: "Adicionar",
      }}
    />
  );
}
