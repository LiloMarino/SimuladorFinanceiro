import type { ReactNode } from "react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { MARKET_PRICE, NAV_PER_QUOTA, NET_WORTH } from "@/shared/lib/fund-metrics";
import type { FundRoomItem, Pending } from "@/types";
import { roomPendingCount } from "../lib/fund-room";
import { FundRoomRow } from "./fund-room-row";

type FundRoomBlockProps = {
  title: string;
  /** Diz o que o bloco abre para o jogador */
  hint: string;
  tone: "fund" | "secondary";
  funds: FundRoomItem[];
  userId: number;
  /** As pendências do jogador, de onde sai a contagem de decisões de cada gestora */
  pending: Pending[];
  /** O que vem sob a tabela: o aviso do bloco */
  footer?: ReactNode;
};

/** Um bloco da lista da sala: o título com a contagem, a frase que explica o bloco e a tabela das gestoras. */
export function FundRoomBlock({ title, hint, tone, funds, userId, pending, footer }: FundRoomBlockProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-2">
            {title}
            <Badge variant={tone === "fund" ? "fund" : "secondary"} size="tag">
              {funds.length}
            </Badge>
          </span>
        </CardTitle>
        <CardDescription>{hint}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead wrap>Gestora</TableHead>
                <TableHead>Etapa</TableHead>
                <TableHead numeric>
                  <MetricLabel metric={NET_WORTH} />
                </TableHead>
                <TableHead numeric>
                  <MetricLabel metric={NAV_PER_QUOTA} />
                </TableHead>
                <TableHead numeric>
                  <MetricLabel metric={MARKET_PRICE} />
                </TableHead>
                <TableHead numeric>Sua parte</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {funds.map((fund) => (
                <FundRoomRow
                  key={fund.id}
                  fund={fund}
                  userId={userId}
                  pendingCount={roomPendingCount(pending, fund.id)}
                />
              ))}
            </TableBody>
          </Table>
          {footer}
        </div>
      </CardContent>
    </Card>
  );
}
