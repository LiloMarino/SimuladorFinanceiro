import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { HOLDING_CLASSES } from "../lib/fund-classes";

type Positions = NonNullable<FundDetails["positions"]>;

/** As posições da carteira da gestora: ativo, classe, quantidade, valor e fatia do patrimônio. */
export function FundPositionsTable({ positions }: { positions: Positions }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead wrap>Ativo</TableHead>
          <TableHead>Classe</TableHead>
          <TableHead numeric>Quantidade</TableHead>
          <TableHead numeric>Valor</TableHead>
          <TableHead numeric>Fatia</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {positions.map((position) => (
          <TableRow key={`${position.asset_class}-${position.ticker ?? position.name}`}>
            <TableCell wrap>
              <span className="grid">
                <b className="font-semibold">{position.ticker ?? position.name}</b>
                {position.ticker && <span className="text-xs text-muted-foreground">{position.name}</span>}
              </span>
            </TableCell>
            <TableCell>{HOLDING_CLASSES[position.asset_class].label}</TableCell>
            <TableCell numeric>{position.quantity === null ? "—" : displayQuantity(position.quantity)}</TableCell>
            <TableCell numeric>{displayMoney(position.value)}</TableCell>
            <TableCell numeric>{displayPercent(position.fraction, 1)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
