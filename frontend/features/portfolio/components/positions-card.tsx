import { Link, useNavigate } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardHeader } from "@/shared/components/ui/card";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { displayMoney, displayPercent, displayRateLabel } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";

/** Resultado com sinal e cor: verde ganhando, vermelho perdendo. */
function Result({ value, pct }: { value: string; pct: string }) {
  const positive = Number(value) >= 0;
  return (
    <span className={positive ? "grid text-right text-success" : "grid text-right text-destructive"}>
      <span className="font-mono">
        {positive ? "+" : ""}
        {displayMoney(value)}
      </span>
      <span className="font-mono text-xs">
        {positive ? "▲" : "▼"} {displayPercent(pct)}
      </span>
    </span>
  );
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
  const stocks = portfolio.variable_income;
  const bonds = portfolio.fixed_income;

  return (
    <Card>
      <Tabs defaultValue="stocks">
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
            <span className="text-xs text-muted-foreground">Clique numa linha pra negociar</span>
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
                  <TableHead>Ativo</TableHead>
                  <TableHead numeric>Qtd.</TableHead>
                  <TableHead numeric>Preço médio</TableHead>
                  <TableHead numeric>Preço atual</TableHead>
                  <TableHead numeric>Valor</TableHead>
                  <TableHead numeric>% carteira</TableHead>
                  <TableHead numeric>Resultado</TableHead>
                  <TableHead>
                    <span className="sr-only">Abrir</span>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stocks.map((p) => (
                  <TableRow key={p.ticker} onActivate={() => navigate(`/variable-income/${p.ticker}`)}>
                    <TableCell>
                      <div className="grid">
                        <span className="font-mono font-semibold">{p.ticker}</span>
                        <span className="text-xs text-muted-foreground">{p.name}</span>
                      </div>
                    </TableCell>
                    <TableCell numeric>{p.size}</TableCell>
                    <TableCell numeric>{displayMoney(p.avg_price)}</TableCell>
                    <TableCell numeric>{displayMoney(p.current_price)}</TableCell>
                    <TableCell numeric>{displayMoney(p.current_value)}</TableCell>
                    <TableCell numeric>{displayPercent(p.portfolio_pct)}</TableCell>
                    <TableCell>
                      <Result value={p.return_value} pct={p.return_pct} />
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
                  <TableHead>Título</TableHead>
                  <TableHead numeric>Aplicado</TableHead>
                  <TableHead numeric>Valor atual</TableHead>
                  <TableHead>Taxa</TableHead>
                  <TableHead numeric>% carteira</TableHead>
                  <TableHead numeric>Resultado</TableHead>
                  <TableHead>
                    <span className="sr-only">Abrir</span>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {bonds.map((p) => (
                  <TableRow key={p.asset.asset_uuid} onActivate={() => navigate(`/fixed-income/${p.asset.asset_uuid}`)}>
                    <TableCell>
                      <span className="grid">
                        <span className="font-semibold">{p.asset.name}</span>
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
                    <TableCell>
                      <ChevronRight className="size-4 text-faint-foreground" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TabsContent>
      </Tabs>
    </Card>
  );
}
