import { Link } from "react-router-dom";
import { FundMark } from "@/shared/components/fund-mark";
import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayIsoDate, displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { FundOffers } from "@/types";
import { closedKindLabel, marketGapLabel } from "../lib/fund-offers";

type ClosedOffersTableProps = { offers: FundOffers["closed"] };

/** As vendas encerradas, cada uma com o preço que se pagou na oferta e o de hoje no mercado. */
export function ClosedOffersTable({ offers }: ClosedOffersTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Gestora</TableHead>
          <TableHead>Tipo</TableHead>
          <TableHead numeric>Preço da oferta</TableHead>
          <TableHead numeric>Vendidas</TableHead>
          <TableHead numeric>Encerrada em</TableHead>
          <TableHead numeric>Preço no mercado hoje</TableHead>
          <TableHead />
        </TableRow>
      </TableHeader>
      <TableBody>
        {offers.map((offer) => {
          const gap = marketGapLabel(offer);
          return (
            <TableRow key={`${offer.fund_id}-${offer.kind}-${offer.closed_on}`}>
              {/* Gestora */}
              <TableCell>
                <Link to={`/funds/${offer.fund_id}`} className="flex items-center gap-2.5 hover:text-primary">
                  <FundMark name={offer.name} size="md" />
                  <span className="grid min-w-0">
                    <b className="font-semibold">{offer.name}</b>
                    <span className="text-xs text-muted-foreground">{offer.ticker}</span>
                  </span>
                </Link>
              </TableCell>
              <TableCell>{closedKindLabel(offer)}</TableCell>
              <TableCell numeric>{displayMoney(offer.price)}</TableCell>
              <TableCell numeric>
                {displayQuantity(offer.sold)} de {displayQuantity(offer.quotas)}
              </TableCell>
              <TableCell numeric>{displayIsoDate(offer.closed_on)}</TableCell>
              <TableCell numeric>
                {offer.market_price === null ? "—" : displayMoney(offer.market_price)}
                {gap !== null && <span className="block font-sans text-xs text-muted-foreground">{gap}</span>}
              </TableCell>
              <TableCell>
                <Button
                  variant="outline"
                  size="sm"
                  nativeButton={false}
                  render={<Link to={`/variable-income/${offer.ticker}`} />}
                >
                  Ver cota
                </Button>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
