import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { cn } from "@/shared/lib/utils";
import {
  displayBytes,
  displayNumber,
  displayPercent,
} from "@/shared/lib/utils/display";
import type { TrafficItem } from "@/types";
import { isHeavy } from "../lib/stats";

interface TrafficTableProps {
  traffic: TrafficItem[];
}

/** O que o servidor envia a cada jogador: não gasta tempo do servidor, gasta volume. */
export function TrafficTable({ traffic }: TrafficTableProps) {
  const sorted = [...traffic].sort((a, b) => b.bytes_per_s - a.bytes_per_s);
  const total = sorted.reduce((sum, item) => sum + item.bytes_per_s, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>O que vai para o navegador</CardTitle>
        <CardDescription>
          Mensagens que o servidor envia a cada jogador. É o que pesa no
          navegador em velocidade alta: a 100× o volume fica 10 vezes maior.
        </CardDescription>
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Evento</TableHead>
            <TableHead numeric>Msg/s</TableHead>
            <TableHead numeric>
              <span className="font-semibold text-foreground">
                Volume <span className="text-[10px]">▼</span>
              </span>
            </TableHead>
            <TableHead numeric>Por mensagem</TableHead>
            <TableHead numeric>Fatia</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.length === 0 && (
            <TableEmptyRow colSpan={5}>
              <span className="text-muted-foreground">Nada enviado ainda.</span>
            </TableEmptyRow>
          )}
          {sorted.map((item) => {
            const share = total > 0 ? item.bytes_per_s / total : 0;
            return (
              <TableRow key={item.event}>
                <TableCell>
                  <span className="font-mono text-[13px]">{item.event}</span>
                </TableCell>
                <TableCell numeric>
                  {displayNumber(item.msgs_per_s, item.msgs_per_s < 10 ? 1 : 0)}
                </TableCell>
                <TableCell numeric>
                  <span className="font-semibold">
                    {displayBytes(item.bytes_per_s)}/s
                  </span>
                </TableCell>
                <TableCell numeric>
                  <span className={cn(isHeavy(item) && "text-warning")}>
                    {displayBytes(item.bytes_per_msg)}
                  </span>
                </TableCell>
                <TableCell numeric>
                  <span className="inline-flex items-center justify-end gap-2">
                    <span className="inline-block h-1.5 w-14 overflow-hidden rounded-full bg-muted">
                      <span
                        className="block h-full rounded-full bg-primary"
                        style={{ width: `${share * 100}%` }}
                      />
                    </span>
                    <span className="w-10 text-right">
                      {share > 0 && share < 0.01
                        ? "< 1%"
                        : displayPercent(share, 0)}
                    </span>
                  </span>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
