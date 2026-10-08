import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent, isLoss } from "@/shared/lib/utils/display";
import { Eye } from "lucide-react";
import { Link } from "react-router-dom";
import type { PortfolioPosition } from "@/types";

interface VariableIncomeTableProps {
  variablePositions: PortfolioPosition[];
}

export function VariableIncomeTable({ variablePositions }: VariableIncomeTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Renda Variável</CardTitle>
      </CardHeader>

      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {[
                "Ativo",
                "Preço Médio",
                "Preço Atual",
                "Quantidade",
                "Valor Total",
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
            {variablePositions.map((pos) => (
              <TableRow key={pos.ticker} className="text-center [&>td]:py-4">
                <TableCell>{pos.ticker}</TableCell>
                <TableCell>{displayMoney(pos.avg_price)}</TableCell>
                <TableCell>{displayMoney(pos.current_price)}</TableCell>
                <TableCell>{pos.size}</TableCell>
                <TableCell>{displayMoney(pos.current_value)}</TableCell>
                <TableCell>{displayPercent(pos.portfolio_pct)}</TableCell>
                <TableCell className={isLoss(pos.return_value) ? "text-destructive" : "text-success"}>
                  {displayMoney(pos.return_value)}
                </TableCell>
                <TableCell className={isLoss(pos.return_value) ? "text-destructive" : "text-success"}>
                  {displayPercent(pos.return_pct)}
                </TableCell>
                <TableCell>
                  <Link
                    to={`/variable-income/${pos.ticker}`}
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
