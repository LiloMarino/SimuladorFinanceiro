import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardHeader } from "@/shared/components/ui/card";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { DailyLiquidityBadge } from "@/shared/components/daily-liquidity-badge";
import { InfoHint } from "@/shared/components/info-hint";
import { MetricHint } from "@/shared/components/metric-hint";
import { DIVIDEND_YIELD, YIELD_ON_COST } from "@/shared/lib/dividend-metrics";
import { MARK_TO_MARKET } from "@/shared/lib/treasury-metrics";
import { displayMoney, displayPercent, displayQuantity, displayRateLabel } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";

/** A base da coluna "% do investido": renda variável e renda fixa, sem o caixa. */
const investedShareHint = (
  <InfoHint label="Como ler o % do investido">
    <div className="grid gap-1 text-left text-xs leading-snug">
      <span>Quanto da sua carteira investida (ações e renda fixa) está nesta posição. O caixa fica de fora.</span>
      <span>Ex.: R$ 10.000 numa posição, de R$ 40.000 investidos, são 25%.</span>
    </div>
  </InfoHint>
);

const isTreasury = (position: PortfolioState["fixed_income"][number]) =>
  position.asset.investment_type === "Tesouro Direto";

/** Marcação do Tesouro com sinal e cor; título sem marcação mostra traço. */
function Mark({ position }: { position: PortfolioState["fixed_income"][number] }) {
  const mark = Number(position.mark);
  if (!isTreasury(position) || mark === 0) return <span className="text-faint-foreground">—</span>;
  return (
    <span className={mark > 0 ? "font-mono text-success" : "font-mono text-destructive"}>
      {mark > 0 ? "+" : "−"}
      {displayMoney(Math.abs(mark))}
    </span>
  );
}

/** Resultado com sinal e cor: verde ganhando, vermelho perdendo. */
function Result({ value, pct, dividends }: { value: string; pct: string; dividends?: string }) {
  const positive = Number(value) >= 0;
  return (
    <span className="grid text-right">
      <span className={positive ? "grid text-success" : "grid text-destructive"}>
        <span className="font-mono">
          {positive ? "+" : ""}
          {displayMoney(value)}
        </span>
        <span className="font-mono text-xs">
          {positive ? "▲" : "▼"} {displayPercent(pct)}
        </span>
      </span>
      {dividends !== undefined && Number(dividends) > 0 && (
        <span className="font-mono text-xs text-dividend">+{displayMoney(dividends)} em proventos</span>
      )}
    </span>
  );
}

/** Rendimento em proventos; sem valor (cripto) a posição não paga. */
function YieldCell({ value }: { value: string | null }) {
  if (value === null) return <span className="font-sans text-xs text-muted-foreground">não paga</span>;
  return <b>{displayPercent(value, 1)}</b>;
}

function EmptyPositions({
  title,
  description,
  to,
  action,
}: {
  title: string;
  description: string;
  to: string;
  action: string;
}) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyTitle>{title}</EmptyTitle>
        <EmptyDescription>{description}</EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button variant="outline" size="sm" nativeButton={false} render={<Link to={to} />}>
          {action}
        </Button>
      </EmptyContent>
    </Empty>
  );
}

/** As posições, renda variável e renda fixa em abas; a linha leva à negociação. */
export function PositionsCard({ portfolio }: { portfolio: PortfolioState }) {
  const navigate = useNavigate();
  const stockSort = useTableSort(portfolio.variable_income, {
    name: (p) => p.ticker,
    quantity: (p) => Number(p.size),
    average: (p) => Number(p.avg_price),
    price: (p) => Number(p.current_price),
    value: (p) => Number(p.current_value),
    share: (p) => Number(p.portfolio_pct),
    yield: (p) => Number(p.dividend_yield_12m ?? -1),
    yieldOnCost: (p) => Number(p.yield_on_cost ?? -1),
    result: (p) => Number(p.return_value),
  });
  const bondSort = useTableSort(portfolio.fixed_income, {
    name: (p) => p.asset.name,
    applied: (p) => Number(p.total_applied),
    value: (p) => Number(p.current_value),
    rate: (p) => Number(p.asset.interest_rate),
    share: (p) => Number(p.portfolio_pct),
    result: (p) => Number(p.return_value),
    mark: (p) => Number(p.mark),
  });
  const stocks = stockSort.rows;
  const bonds = bondSort.rows;
  const [tab, setTab] = useState("stocks");
  const redeemable = Number(portfolio.fixed_income_redeemable);
  const hasTreasury = bonds.some(isTreasury);

  return (
    <Card>
      <Tabs value={tab} onValueChange={setTab}>
        <CardHeader>
          <TabsList variant="line">
            <TabsTrigger value="stocks">
              Renda variável{" "}
              <Badge variant="secondary" size="sm">
                {stocks.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="bonds">
              Renda fixa{" "}
              <Badge variant="secondary" size="sm">
                {bonds.length}
              </Badge>
            </TabsTrigger>
          </TabsList>
          <CardAction>
            <span className="text-xs text-muted-foreground">
              {tab === "bonds" && redeemable > 0 && (
                <>
                  <b className="font-mono font-semibold text-success">{displayMoney(redeemable)}</b> resgatáveis hoje
                  ·{" "}
                </>
              )}
              Clique numa linha pra negociar
            </span>
          </CardAction>
        </CardHeader>

        <TabsContent value="stocks">
          {stocks.length === 0 ? (
            <EmptyPositions
              title="Nenhuma ação na carteira"
              description="Escolha uma ação na lista e envie uma ordem de compra."
              to="/variable-income"
              action="Ver ações"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <SortableTableHead {...stockSort.header("name")} label="Ativo" />
                  <SortableTableHead {...stockSort.header("quantity")} label="Qtd." numeric />
                  <SortableTableHead {...stockSort.header("average")} label="Preço médio" numeric />
                  <SortableTableHead {...stockSort.header("price")} label="Preço atual" numeric />
                  <SortableTableHead {...stockSort.header("value")} label="Valor" numeric />
                  <SortableTableHead
                    {...stockSort.header("share")}
                    label="% do investido"
                    numeric
                    hint={investedShareHint}
                  />
                  <SortableTableHead
                    {...stockSort.header("yield")}
                    label="DY 12m"
                    numeric
                    variant="tinted"
                    hint={<MetricHint metric={DIVIDEND_YIELD} />}
                  />
                  <SortableTableHead
                    {...stockSort.header("yieldOnCost")}
                    label="YoC"
                    numeric
                    variant="tinted"
                    hint={<MetricHint metric={YIELD_ON_COST} />}
                  />
                  <SortableTableHead {...stockSort.header("result")} label="Resultado" numeric />
                  <TableHead>
                    <span className="sr-only">Abrir</span>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stocks.map((p) => (
                  <TableRow key={p.ticker} onActivate={() => void navigate(`/variable-income/${p.ticker}`)}>
                    <TableCell>
                      <div className="grid">
                        <span className="font-mono font-semibold">{p.ticker}</span>
                        <span className="text-xs text-muted-foreground">{p.name}</span>
                      </div>
                    </TableCell>
                    <TableCell numeric>{displayQuantity(p.size)}</TableCell>
                    <TableCell numeric>{displayMoney(p.avg_price)}</TableCell>
                    <TableCell numeric>{displayMoney(p.current_price)}</TableCell>
                    <TableCell numeric>{displayMoney(p.current_value)}</TableCell>
                    <TableCell numeric>{displayPercent(p.portfolio_pct)}</TableCell>
                    <TableCell numeric tinted>
                      <YieldCell value={p.dividend_yield_12m} />
                    </TableCell>
                    <TableCell numeric tinted>
                      {p.yield_on_cost === null ? "—" : displayPercent(p.yield_on_cost, 1)}
                    </TableCell>
                    <TableCell>
                      <Result value={p.return_value} pct={p.return_pct} dividends={p.dividends_received} />
                    </TableCell>
                    <TableCell>
                      <ChevronRight className="size-4 text-faint-foreground" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TabsContent>

        <TabsContent value="bonds">
          {bonds.length === 0 ? (
            <EmptyPositions
              title="Nenhum título na carteira"
              description="Compare os títulos de renda fixa e invista no que render mais pra você."
              to="/fixed-income"
              action="Ver renda fixa"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <SortableTableHead {...bondSort.header("name")} label="Título" />
                  <SortableTableHead {...bondSort.header("applied")} label="Aplicado" numeric />
                  <SortableTableHead {...bondSort.header("value")} label="Valor atual" numeric />
                  <SortableTableHead {...bondSort.header("rate")} label="Taxa" />
                  <SortableTableHead
                    {...bondSort.header("share")}
                    label="% do investido"
                    numeric
                    hint={investedShareHint}
                  />
                  <SortableTableHead {...bondSort.header("result")} label="Resultado" numeric />
                  <SortableTableHead
                    {...bondSort.header("mark")}
                    label="Marcação"
                    numeric
                    hint={<MetricHint metric={MARK_TO_MARKET} />}
                  />
                  <TableHead>
                    <span className="sr-only">Abrir</span>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {bonds.map((p) => (
                  <TableRow
                    key={p.asset.asset_uuid}
                    onActivate={() =>
                      void navigate(isTreasury(p) ? "/treasury" : `/fixed-income/${p.asset.asset_uuid}`)
                    }
                  >
                    <TableCell>
                      <span className="grid">
                        <span className="flex items-center gap-1.5 font-semibold">
                          {p.asset.name}
                          {p.asset.daily_liquidity && (
                            <DailyLiquidityBadge size="sm">liquidez diária</DailyLiquidityBadge>
                          )}
                        </span>
                        <span className="text-xs text-muted-foreground">{p.asset.issuer}</span>
                      </span>
                    </TableCell>
                    <TableCell numeric>{displayMoney(p.total_applied)}</TableCell>
                    <TableCell numeric>{displayMoney(p.current_value)}</TableCell>
                    <TableCell>{displayRateLabel(p.asset.rate_index, p.asset.interest_rate)}</TableCell>
                    <TableCell numeric>{displayPercent(p.portfolio_pct)}</TableCell>
                    <TableCell>
                      <Result value={p.return_value} pct={p.return_pct} />
                    </TableCell>
                    <TableCell numeric>
                      <Mark position={p} />
                    </TableCell>
                    <TableCell>
                      {p.asset.daily_liquidity ? (
                        <Button
                          variant="outline"
                          size="sm"
                          nativeButton={false}
                          render={
                            <Link
                              to={`/fixed-income/${p.asset.asset_uuid}?tab=redeem`}
                              onClick={(e) => e.stopPropagation()}
                            />
                          }
                        >
                          Resgatar
                        </Button>
                      ) : (
                        <ChevronRight className="size-4 text-faint-foreground" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {bonds.length > 0 && hasTreasury && (
            <div className="border-t px-4 py-3">
              <Link to="/treasury" className="text-sm font-medium text-primary hover:text-primary-hover">
                Vender os títulos do Tesouro na tela do Tesouro ›
              </Link>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </Card>
  );
}
