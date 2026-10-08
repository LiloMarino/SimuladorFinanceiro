import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent, displayRateLabel, isLoss } from "@/shared/lib/utils/display";
import { Eye } from "lucide-react";
import { Link } from "react-router-dom";
import type { FixedIncomePosition } from "@/types";

interface FixedIncomeTableProps {
  fixedPositions: FixedIncomePosition[];
}

export function FixedIncomeTable({ fixedPositions }: FixedIncomeTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Renda Fixa</CardTitle>
      </CardHeader>

      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {[
                "Ativo",
                "Valor Investido",
                "Valor Atual",
                "Taxa",
                "% Carteira",
                "Retorno (R$)",
                "Retorno (%)",
                "Ações",
              ].map((h) => (
                <TableHead key={h} className="text-center">
                  {h}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>

          <TableBody>
            {fixedPositions.map((pos) => (
              <TableRow key={pos.asset.asset_uuid} className="text-center [&>td]:py-4">
                <TableCell>{pos.asset.name}</TableCell>
                <TableCell>{displayMoney(pos.total_applied)}</TableCell>
                <TableCell>{displayMoney(pos.current_value)}</TableCell>
                <TableCell>{displayRateLabel(pos.asset.rate_index, pos.asset.interest_rate)}</TableCell>
                <TableCell>{displayPercent(pos.portfolio_pct)}</TableCell>
                <TableCell className={isLoss(pos.return_value) ? "text-destructive" : "text-success"}>
                  {displayMoney(pos.return_value)}
                </TableCell>
                <TableCell className={isLoss(pos.return_value) ? "text-destructive" : "text-success"}>
                  {displayPercent(pos.return_pct)}
                </TableCell>
                <TableCell>
                  <Link
                    to={`/fixed-income/${pos.asset.asset_uuid}`}
                    className="text-blue-600 hover:text-blue-800 text-sm flex items-center justify-center"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    Detalhes
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
