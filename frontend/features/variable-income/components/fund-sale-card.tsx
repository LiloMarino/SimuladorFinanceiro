import { Megaphone } from "lucide-react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { fundStage } from "@/shared/lib/fund-view";
import { displayIsoDate, displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";

type SaleCardView = {
  title: string;
  badge: string;
  price: string;
  sold: number;
  total: number;
  endsOn: string | null;
};

/** A venda de cotas novas em aberto: a oferta pública ou a sobra da emissão, as duas a preço fixo. */
function openSaleOf(fund: FundDetails): SaleCardView | null {
  if (fundStage(fund) === "offer" && fund.offer_quotas !== null && fund.offer_price !== null) {
    return {
      title: "Oferta pública em andamento",
      badge: `pregão ${fund.offer_session ?? 1} de 5`,
      price: fund.offer_price,
      sold: Number(fund.offer_sold ?? 0),
      total: Number(fund.offer_quotas),
      endsOn: fund.offer_ends_on,
    };
  }
  const issuance = fund.issuance;
  if (issuance !== null && issuance.closed_on === null && issuance.phase === "leftover") {
    return {
      title: "Sobra da emissão em andamento",
      badge: "sobra aberta",
      price: issuance.price,
      sold: Number(issuance.sold),
      total: Number(issuance.quotas),
      endsOn: issuance.ends_on,
    };
  }
  return null;
}

/** O que a gestora ainda vende: preço fixo, quanto sobra e até quando. */
export function FundSaleCard({ fund }: { fund: FundDetails }) {
  const sale = openSaleOf(fund);
  if (sale === null) return null;

  const remaining = Math.max(sale.total - sale.sold, 0);

  return (
    <Card variant="info">
      <CardContent>
        <div className="grid gap-3">
          <div className="flex items-center gap-2.5">
            <Megaphone className="size-4 text-primary" />
            <b className="text-[15px] font-semibold">{sale.title}</b>
            <Badge variant="success" size="tag">
              {sale.badge}
            </Badge>
          </div>
          <Progress value={sale.total > 0 ? (sale.sold / sale.total) * 100 : 0} aria-label="Cotas vendidas" />
          <div>
            <KeyValueRow label="Preço fixo por cota" value={displayMoney(sale.price)} />
            <KeyValueRow
              label="Ainda à venda"
              value={`${displayQuantity(String(remaining))} de ${displayQuantity(String(sale.total))} cotas`}
            />
            {sale.endsOn && <KeyValueRow label="Vai até" value={displayIsoDate(sale.endsOn)} />}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
