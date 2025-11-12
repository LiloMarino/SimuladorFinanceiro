import type { FixedIncomeAsset } from "@/types";
import BaseCard from "./base-card";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface FixedIncomeCardProps {
  asset: FixedIncomeAsset;
}

export default function FixedIncomeCard({ asset }: FixedIncomeCardProps) {
  const maturityDate = asset.maturityDate ? format(new Date(asset.maturityDate), "dd/MM/yyyy", { locale: ptBR }) : "—";
  const daysLabel = asset.daysToMaturity ? ` (${asset.daysToMaturity} dias)` : "";
  const rateLabel =
    asset.rateIndex === "PREFIXADO"
      ? `${asset.interestRate?.toFixed(2)}% a.a.`
      : asset.interestRate
      ? `${asset.interestRate}% ${asset.rateIndex}`
      : asset.rateIndex;

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
            {rateLabel}
          </Badge>
        ),
      }}
      fields={[
        { label: "Vencimento:", value: maturityDate + daysLabel },
        { label: "Índice:", value: asset.rateIndex },
        { label: "IR:", value: asset.incomeTax ?? "—" },
      ]}
      footer={{
        linkTo: `/fixed-income/${asset.name.toLowerCase()}`,
        label: "Adicionar",
      }}
    />
  );
}
