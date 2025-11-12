import type { FixedIncomeAsset } from "@/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface FixedIncomeCardProps {
  asset: FixedIncomeAsset;
}

export default function FixedIncomeCard({ asset }: FixedIncomeCardProps) {
  const maturityDate = asset.maturityDate ? format(new Date(asset.maturityDate), "dd/MM/yyyy", { locale: ptBR }) : "—";

  const daysLabel = asset.daysToMaturity ? ` (${asset.daysToMaturity} dias)` : "";
  const taxLabel = asset.incomeTax ?? "—";
  const rateLabel =
    asset.rateIndex === "PREFIXADO"
      ? `${asset.interestRate?.toFixed(2)}% a.a.`
      : asset.interestRate
      ? `${asset.interestRate}% ${asset.rateIndex}`
      : asset.rateIndex;

  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden transition-transform transform hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200"
      data-asset={asset.name}
    >
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex justify-between items-center">
          <h3 className="font-bold text-lg">{asset.name}</h3>
          <Badge variant="outline" className="text-green-600 border-green-300 font-medium">
            {rateLabel}
          </Badge>
        </div>
        <p className="text-gray-500 text-sm">
          Emitido por: <span className="font-medium">{asset.issuer}</span>
        </p>
      </div>

      {/* Conteúdo */}
      <div className="p-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-500">Vencimento:</span>
          <span className="font-medium">{maturityDate + daysLabel}</span>
        </div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-500">Índice:</span>
          <span className="font-medium">{asset.rateIndex}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">IR:</span>
          <span className="font-medium">{taxLabel}</span>
        </div>
      </div>

      {/* Link de ação */}
      <div className="bg-gray-50 px-4 py-2 flex justify-end">
        <Link
          to={`/fixed-income/${asset.name.toLowerCase()}`}
          className="text-blue-600 text-sm font-medium hover:text-blue-800"
        >
          Adicionar
        </Link>
      </div>
    </div>
  );
}
