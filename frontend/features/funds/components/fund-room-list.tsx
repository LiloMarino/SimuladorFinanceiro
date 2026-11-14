import { Link } from "react-router-dom";
import { FundMark } from "@/shared/components/fund-mark";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { FundSummary } from "@/types";
import { premium } from "../lib/fund-math";
import { MARKET_PRICE, NAV_PER_QUOTA, PREMIUM } from "../lib/fund-metrics";
import { fundStage } from "../lib/fund-view";
import { FundSection } from "./fund-section";

const STAGE_LABEL = { closed: "Fechada", offer: "Oferta aberta", listed: "Negociada" } as const;

/** As gestoras da sala, cada uma com o preço, o patrimônio por cota e o ágio de hoje. */
export function FundRoomList({ funds }: { funds: FundSummary[] }) {
  return (
    <FundSection title="Gestoras da sala">
      {funds.length === 0 ? (
        <p className="text-[13px] text-muted-foreground">
          Ninguém fundou uma gestora ainda. A primeira a nascer aparece aqui.
        </p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead wrap>Gestora</TableHead>
              <TableHead>Etapa</TableHead>
              <TableHead numeric>
                <MetricLabel metric={MARKET_PRICE} />
              </TableHead>
              <TableHead numeric>
                <MetricLabel metric={NAV_PER_QUOTA} />
              </TableHead>
              <TableHead numeric>
                <MetricLabel metric={PREMIUM} />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {funds.map((fund) => {
              const price = fund.price === null ? null : Number(fund.price);
              const nav = fund.nav === null ? null : Number(fund.nav);
              return (
                <TableRow key={fund.id}>
                  <TableCell wrap>
                    <Link to={`/funds/${fund.id}`} className="flex items-center gap-2.5 hover:text-primary">
                      <FundMark name={fund.name} />
                      <span className="grid min-w-0">
                        <b className="line-clamp-2 font-semibold break-words">{fund.name}</b>
                        <span className="text-xs text-muted-foreground">
                          <span className="font-mono">{fund.ticker}</span>
                          {fund.manager_nickname && <> · gerida por {fund.manager_nickname}</>}
                        </span>
                      </span>
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Badge variant={fundStage(fund) === "closed" ? "secondary" : "success"} size="tag">
                      {STAGE_LABEL[fundStage(fund)]}
                    </Badge>
                  </TableCell>
                  <TableCell numeric>{price === null ? "—" : displayMoney(price)}</TableCell>
                  <TableCell numeric>{nav === null ? "—" : displayMoney(nav)}</TableCell>
                  <TableCell numeric>
                    {price === null || nav === null ? (
                      "—"
                    ) : (
                      <b className="font-semibold">{displaySignedPercent(premium(price, nav), 1)}</b>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </FundSection>
  );
}
