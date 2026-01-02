import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import { faEye } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link } from "react-router-dom";
import type { VariablePosition } from "../lib/portfolio-calculator";

interface VariableIncomeTableProps {
  variablePositions: VariablePosition[];
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
                <TableCell>{displayMoney(pos.averagePrice)}</TableCell>
                <TableCell>{displayMoney(pos.currentPrice)}</TableCell>
                <TableCell>{pos.quantity}</TableCell>
                <TableCell>{displayMoney(pos.currentValue)}</TableCell>
                <TableCell>{displayPercent(pos.portfolioPercent)}</TableCell>
                <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                  {displayMoney(pos.returnValue)}
                </TableCell>
                <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                  {displayPercent(pos.returnPercent)}
                </TableCell>
                <TableCell>
                  <Link
                    to={`/variable-income/${pos.ticker}`}
                    className="text-blue-600 hover:text-blue-800 text-sm flex items-center justify-center"
                  >
                    <FontAwesomeIcon icon={faEye} className="mr-1" />
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
