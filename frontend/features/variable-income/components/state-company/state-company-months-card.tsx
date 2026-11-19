import { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayMonthShort, displayShortMonthYear } from "@/shared/lib/utils/display";
import type { StateCompanyMonth } from "@/types";
import { nextCloseNote, reasonText } from "../../lib/state-company";

const LATEST = 5;
const EMPTY = "—";

/** Uma linha do mês; a tabela de todos os meses leva o ano, porque passa de um. */
function MonthRow({ item, withYear }: { item: StateCompanyMonth; withYear: boolean }) {
  const profit = item.profit === null ? null : Number(item.profit);

  return (
    <TableRow>
      <TableCell>{withYear ? displayShortMonthYear(item.month) : displayMonthShort(item.month)}</TableCell>
      <TableCell>
        <span className={cn("font-mono", profit !== null && profit < 0 && "text-destructive")}>
          {profit === null ? EMPTY : displayMoney(profit)}
        </span>
      </TableCell>
      <TableCell>
        <span className="font-mono">{item.dividend === null ? EMPTY : displayMoney(item.dividend)}</span>
      </TableCell>
      <TableCell wrap>{reasonText(item)}</TableCell>
    </TableRow>
  );
}

/** Os últimos meses fechados da estatal, com o lucro, o dividendo e o porquê de cada um; "Ver todos" abre o histórico inteiro. */
export function StateCompanyMonthsCard({ months }: { months: StateCompanyMonth[] }) {
  const [showAll, setShowAll] = useState(false);
  const newestFirst = [...months].reverse();
  const visible = showAll ? newestFirst : newestFirst.slice(0, LATEST);
  const note = nextCloseNote(months);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mês a mês</CardTitle>
        <CardDescription>
          {showAll ? "Todos os meses fechados." : `Os ${LATEST} últimos meses fechados.`} {note}
        </CardDescription>
        {months.length > LATEST && (
          <CardAction>
            <Button size="sm" variant="outline" onClick={() => setShowAll((open) => !open)}>
              {showAll ? "Ver menos" : "Ver todos"}
            </Button>
          </CardAction>
        )}
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead wrap>Mês</TableHead>
              <TableHead wrap>Lucro por ação</TableHead>
              <TableHead wrap>Dividendo por ação</TableHead>
              <TableHead wrap>Por quê</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {visible.map((item) => (
              <MonthRow key={item.month} item={item} withYear={showAll} />
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
