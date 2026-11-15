import { Landmark } from "lucide-react";
import { CardState } from "@/shared/components/card-state";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoneyLarge, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { SovereignPosition } from "@/types";
import { useSovereignFund } from "../../hooks/queries/useSovereignFund";
import { FUND_ROOM, FUND_STAKE } from "../../lib/government-metrics";
import { fundCashLabel } from "../../lib/sovereign-fund";

type SovereignFundCardProps = {
  /** Abre o diálogo do aporte; só o presidente vê o botão */
  onContribute: () => void;
};

/** O Fundo Soberano na aba Estatais: caixa, carteira com a fatia de cada ativo e o que já voltou ao Tesouro. A consulta se resolve aqui. */
export function SovereignFundCard({ onContribute }: SovereignFundCardProps) {
  const { data, error, refetch } = useSovereignFund();

  if (!data) {
    return (
      <CardState
        title="Fundo Soberano"
        label="Carregando o Fundo Soberano"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar o Fundo Soberano"
      >
        <Skeleton className="h-16" />
        <Skeleton className="h-24" />
      </CardState>
    );
  }

  const noCash = Number(data.cash) === 0;

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-4">
          {/* Header */}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-0.5">
              <h2 className="text-[15px] font-semibold">Fundo Soberano</h2>
              <p className="text-[13px] text-muted-foreground">
                A carteira do governo na bolsa: compra ações e cotas de gestora com o caixa dos aportes aprovados, nunca
                mais de {displayPercent(data.ceiling, 0)} de um ativo.
              </p>
            </div>
            {data.is_president && (
              <Button size="sm" variant="outline" onClick={onContribute}>
                <Landmark data-icon="inline-start" />
                Aportar
              </Button>
            )}
          </div>

          {/* Totais do fundo */}
          <dl className="grid grid-cols-2 gap-3 text-[13px] sm:grid-cols-4">
            <Total label="Caixa do fundo" value={fundCashLabel(data.cash)} />
            <Total label="Investido" value={fundCashLabel(data.invested)} />
            <Total label="Aportado" value={fundCashLabel(data.contributed)} />
            <Total label="Devolvido ao Tesouro" value={fundCashLabel(data.returned)} />
          </dl>

          {/* Carteira */}
          {data.positions.length === 0 ? (
            <Empty variant="dashed">
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <Landmark />
                </EmptyMedia>
                <EmptyTitle>{noCash ? "O fundo ainda não tem caixa" : "Nada comprado ainda"}</EmptyTitle>
                <EmptyDescription>
                  {noCash
                    ? "Sem aporte aprovado o fundo não compra nada. O aporte é uma medida de gasto que passa pelo Congresso."
                    : data.is_president
                      ? "Troque o caixa da topbar para o Fundo Soberano e compre na Renda Variável."
                      : "As compras do presidente aparecem aqui e no Jornal."}
                </EmptyDescription>
              </EmptyHeader>
              {data.is_president && noCash && (
                <Button size="sm" onClick={onContribute}>
                  Aportar no fundo
                </Button>
              )}
            </Empty>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead wrap>Ativo</TableHead>
                  <TableHead wrap numeric>
                    Valor hoje
                  </TableHead>
                  <TableHead wrap numeric>
                    Resultado
                  </TableHead>
                  <TableHead wrap numeric>
                    <MetricLabel metric={FUND_STAKE} />
                  </TableHead>
                  <TableHead wrap numeric>
                    <MetricLabel metric={FUND_ROOM} />
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.positions.map((position) => (
                  <PositionRow key={position.ticker} position={position} ceiling={data.ceiling} />
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function Total({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid gap-0.5 rounded-lg border p-3">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="font-mono text-[15px] font-semibold">{value}</dd>
    </div>
  );
}

type PositionRowProps = { position: SovereignPosition; ceiling: string };

function PositionRow({ position, ceiling }: PositionRowProps) {
  const atCeiling = position.room !== null && Number(position.room) === 0;
  const result = Number(position.return_value);

  return (
    <TableRow>
      <TableCell>
        <div className="grid">
          <span className="font-semibold">{position.ticker}</span>
          <span className="text-xs text-muted-foreground">
            {position.name} · {displayQuantity(position.size)} {position.is_fund ? "cotas" : "ações"}
          </span>
        </div>
      </TableCell>
      <TableCell numeric>{displayMoneyLarge(position.current_value)}</TableCell>
      <TableCell numeric tone={result >= 0 ? "success" : undefined}>
        <span className={result < 0 ? "text-destructive" : undefined}>
          {result >= 0 ? "+" : "-"}
          {displayMoneyLarge(Math.abs(result))}
        </span>
      </TableCell>
      <TableCell numeric>
        {position.stake === null ? "sem dado" : displayPercent(position.stake, 1)}
        {atCeiling && <span className="block text-xs text-warning">no teto de {displayPercent(ceiling, 0)}</span>}
      </TableCell>
      <TableCell numeric>{position.room === null ? "—" : displayQuantity(position.room)}</TableCell>
    </TableRow>
  );
}
