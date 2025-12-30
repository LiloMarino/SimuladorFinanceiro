import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { formatMoney, formatPercent } from "@/shared/lib/utils/formatting";
import { faEye } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link } from "react-router-dom";
import type { FixedPosition } from "../lib/portfolio-calculator";

interface FixedIncomeTableProps {
  fixedPositions: FixedPosition[];
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
              <TableRow key={pos.uuid} className="text-center [&>td]:py-4">
                <TableCell>{pos.name}</TableCell>
                <TableCell>{formatMoney(pos.investedValue)}</TableCell>
                <TableCell>{formatMoney(pos.currentValue)}</TableCell>
                <TableCell>{pos.rateLabel}</TableCell>
                <TableCell>{formatPercent(pos.portfolioPercent)}</TableCell>
                <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                  {formatMoney(pos.returnValue)}
                </TableCell>
                <TableCell className={pos.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                  {formatPercent(pos.returnPercent)}
                </TableCell>
                <TableCell>
                  <Link
                    to={`/fixed-income/${pos.uuid}`}
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
