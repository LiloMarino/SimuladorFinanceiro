import { useState, type ReactNode } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Label } from "@/shared/components/ui/label";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Switch } from "@/shared/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { DailyLiquidityBadge } from "@/shared/components/daily-liquidity-badge";
import { ErrorState } from "@/shared/components/error-state";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useBudget } from "@/shared/hooks/queries/useBudget";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useEconomicIndicators } from "@/shared/hooks/queries/useEconomicIndicators";
import {
  displayDate,
  displayMoney,
  displayMonthName,
  displayPercent,
  displayRateLabel,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { FixedIncomeOffer } from "@/types";
import { useFixedIncomeAssets } from "../hooks/queries/useFixedIncomeAssets";
import { displayCap, isPermanentCdb, isRareOffer } from "../lib/daily-liquidity";
import { INVESTMENT_TYPE_LABELS, timeToMaturity } from "../lib/labels";
import { hasPremium, isTreasury, purchasePremiumNote } from "../lib/premium";
import { PremiumStrip } from "../components/premium-strip";
import { PremiumTag } from "../components/premium-tag";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber } from "@/shared/lib/table-sort";

// Com a taxa equivalente escondida a tabela perde a coluna "Equivale hoje"
const COLUMNS = 8;
const COLUMNS_WITHOUT_RATE = 7;

type IndexFilter = "ALL" | FixedIncomeOffer["rate_index"];
type TypeFilter = "ALL" | "CDB" | "LCI_LCA" | "Tesouro Direto";

const INDEX_FILTERS: { value: IndexFilter; label: string }[] = [
  { value: "ALL", label: "Todos" },
  { value: "CDI", label: "CDI" },
  { value: "IPCA", label: "IPCA" },
  { value: "SELIC", label: "SELIC" },
  { value: "Prefixado", label: "Prefixado" },
];
const TYPE_FILTERS: { value: TypeFilter; label: string }[] = [
  { value: "ALL", label: "Todos os tipos" },
  { value: "CDB", label: "CDB" },
  { value: "LCI_LCA", label: "LCI/LCA" },
  { value: "Tesouro Direto", label: "Tesouro" },
];

const matchesType = (o: FixedIncomeOffer, filter: TypeFilter) =>
  filter === "ALL" ||
  (filter === "LCI_LCA" ? o.investment_type === "LCI" || o.investment_type === "LCA" : o.investment_type === filter);

export default function FixedIncomePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { data: offers, isLoading, error, refetch } = useFixedIncomeAssets();
  const { data: portfolio } = usePortfolio();
  const { data: simulation } = useSimulationState();
  const { data: indicators } = useEconomicIndicators();
  const { simulation: match } = useSimulation();
  const showRate = match?.simulation?.show_equivalent_rate ?? true;
  const { data: budget } = useBudget({ enabled: !!match?.simulation?.government_enabled });
  const [indexFilter, setIndexFilter] = useState<IndexFilter>("ALL");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("ALL");
  const [onlyExempt, setOnlyExempt] = useState(false);
  const [onlyHeld, setOnlyHeld] = useState(false);
  // O detalhe de um título sem liquidez aponta para cá com o filtro já ligado
  const [onlyDaily, setOnlyDaily] = useState(searchParams.get("liquidity") === "daily");

  const held = new Map((portfolio?.fixed_income ?? []).map((p) => [p.asset.asset_uuid, p]));
  // O CDB de 100% do CDI mora no destaque do topo; a tabela lista o resto da vitrine
  const permanentCdb = (offers ?? []).find(isPermanentCdb);
  const listed = (offers ?? []).filter((o) => o !== permanentCdb);
  const heldCount = listed.filter((o) => held.has(o.asset_uuid)).length;
  const filtered = listed
    .filter((o) => !onlyHeld || held.has(o.asset_uuid))
    .filter((o) => (indexFilter === "ALL" || o.rate_index === indexFilter) && matchesType(o, typeFilter))
    .filter((o) => !onlyExempt || o.tax_exempt)
    .filter((o) => !onlyDaily || o.daily_liquidity);
  const sorting = useTableSort(
    filtered,
    {
      name: (o) => o.name,
      type: (o) => INVESTMENT_TYPE_LABELS[o.investment_type],
      rate: (o) => Number(o.interest_rate),
      equivalent: (o) => sortNumber(o.effective_annual_rate),
      maturity: (o) => o.maturity_date,
      liquidity: (o) => (o.daily_liquidity ? 0 : 1),
      tax: (o) => (o.tax_exempt ? 0 : Number(o.income_tax_rate_at_maturity)),
    },
    showRate ? { column: "equivalent", direction: "desc" } : { column: "maturity", direction: "asc" },
  );
  const visible = sorting.rows;
  const topRate = Math.max(...visible.map((o) => Number(o.effective_annual_rate)), 0.0001);
  const today = simulation?.current_date;

  // Erro ou sem resultado: a tabela fica com o cabeçalho e a mensagem ocupa uma linha
  const message = error ? (
    <ErrorState
      title="Não deu pra carregar os títulos"
      description="A partida continua; tente de novo."
      error={error}
      onRetry={() => void refetch()}
    />
  ) : visible.length === 0 ? (
    <Empty>
      <EmptyHeader>
        {onlyDaily && permanentCdb ? (
          <>
            <EmptyTitle>Nenhuma oferta acima de 100% do CDI com liquidez diária este mês</EmptyTitle>
            <EmptyDescription>O CDB de 100% do CDI, no topo, segue aberto.</EmptyDescription>
          </>
        ) : onlyHeld && heldCount === 0 ? (
          <>
            <EmptyTitle>Nenhum título da lista na carteira</EmptyTitle>
            <EmptyDescription>Os títulos que você comprar aparecem aqui.</EmptyDescription>
          </>
        ) : onlyDaily ? (
          <>
            <EmptyTitle>Nenhum título com liquidez diária nesta partida</EmptyTitle>
            <EmptyDescription>O caixa é o único lugar de onde o dinheiro sai no mesmo dia.</EmptyDescription>
          </>
        ) : (
          <EmptyTitle>
            {offers?.length ? "Nenhum título com esse filtro" : "Nenhum título disponível nesta partida"}
          </EmptyTitle>
        )}
      </EmptyHeader>
    </Empty>
  ) : null;

  const header = (
    <TableHeader>
      <TableRow>
        <SortableTableHead {...sorting.header("name")} label="Título" />
        <SortableTableHead {...sorting.header("type")} label="Tipo" />
        <SortableTableHead {...sorting.header("rate")} label="Rentabilidade" />
        {showRate && <SortableTableHead {...sorting.header("equivalent")} label="Equivale hoje" />}
        <SortableTableHead {...sorting.header("maturity")} label="Vencimento" />
        <SortableTableHead {...sorting.header("liquidity")} label="Resgate" />
        <SortableTableHead {...sorting.header("tax")} label="IR" />
        <TableHead>
          <span className="sr-only">Investir</span>
        </TableHead>
      </TableRow>
    </TableHeader>
  );

  const renderBody = () => {
    if (isLoading) {
      // O esqueleto mantém as colunas da tabela, com ou sem a taxa equivalente
      const columns = showRate ? COLUMNS : COLUMNS_WITHOUT_RATE;
      return (
        <Table>
          {header}
          <TableBody>
            {Array.from({ length: 5 }, (_, row) => (
              <TableRow key={row}>
                {Array.from({ length: columns }, (_, column) => (
                  <TableCell key={column}>
                    {column === 0 ? (
                      <div className="grid gap-1.5">
                        <Skeleton className="h-3.5 w-3/5" />
                        <Skeleton className="h-2.5 w-1/3" />
                      </div>
                    ) : (
                      <Skeleton className="h-5 w-14" />
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      );
    }
    return (
      <Table>
        {header}
        <TableBody>
          {message && <TableEmptyRow colSpan={showRate ? COLUMNS : COLUMNS_WITHOUT_RATE}>{message}</TableEmptyRow>}
          {visible.map((o) => {
            const position = held.get(o.asset_uuid);
            return (
              <TableRow key={o.asset_uuid} onActivate={() => void navigate(`/fixed-income/${o.asset_uuid}`)}>
                <TableCell>
                  <div className="grid">
                    <span className="flex items-center gap-2 font-semibold">
                      <span className="max-w-[300px] truncate">{o.name}</span>
                      {held.has(o.asset_uuid) && (
                        <Badge variant="info" size="sm">
                          na carteira
                        </Badge>
                      )}
                    </span>
                    {onlyHeld && (
                      <span className="text-xs font-medium text-info">
                        {displayMoney(held.get(o.asset_uuid)?.total_applied ?? 0)} aplicados
                      </span>
                    )}
                    <span className="max-w-[300px] truncate text-xs text-muted-foreground">{o.issuer}</span>
                    {isRareOffer(o) && o.offered_until && o.player_cap && (
                      <span className="text-xs font-medium text-warning">
                        oferta do catálogo de {displayMonthName(o.offered_until)} · até {displayCap(o.player_cap)} por
                        jogador
                      </span>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="secondary">{INVESTMENT_TYPE_LABELS[o.investment_type]}</Badge>
                </TableCell>
                <TableCell>
                  <div className="grid gap-1">
                    <span className="font-mono">{displayRateLabel(o.rate_index, o.interest_rate)}</span>
                    {budget && hasPremium(o) && position && (
                      <span className="text-xs text-muted-foreground">
                        {purchasePremiumNote(position.first_applied_date, o)}
                      </span>
                    )}
                    {budget && !position && hasPremium(o) && <PremiumTag offer={o} budget={budget} />}
                    {budget && !isTreasury(o) && (
                      <span className="text-xs text-muted-foreground">sem prêmio: o prêmio é só do Tesouro</span>
                    )}
                  </div>
                </TableCell>
                {showRate && (
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className="h-1.5 w-22 overflow-hidden rounded-full bg-muted">
                        <span
                          className="block h-full rounded-full bg-success"
                          style={{ width: `${(Number(o.effective_annual_rate) / topRate) * 100}%` }}
                        />
                      </span>
                      <span className="font-mono font-semibold">
                        {o.effective_annual_rate === null ? "—" : `${displayPercent(o.effective_annual_rate)} a.a.`}
                      </span>
                    </div>
                  </TableCell>
                )}
                <TableCell>
                  <div className="grid">
                    <span className="font-mono">{displayDate(parseLocalDate(o.maturity_date))}</span>
                    {today && (
                      <span className="text-xs text-muted-foreground">{timeToMaturity(o.maturity_date, today)}</span>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  {o.daily_liquidity ? (
                    <DailyLiquidityBadge>Qualquer dia</DailyLiquidityBadge>
                  ) : (
                    <span className="text-[13px] text-muted-foreground">No vencimento</span>
                  )}
                </TableCell>
                <TableCell>
                  {o.tax_exempt ? (
                    <Badge variant="success">Isento</Badge>
                  ) : (
                    <Badge variant="secondary">22,5% → {displayPercent(o.income_tax_rate_at_maturity, 1)}</Badge>
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    variant="outline"
                    size="sm"
                    nativeButton={false}
                    render={<Link to={`/fixed-income/${o.asset_uuid}`} onClick={(e) => e.stopPropagation()} />}
                  >
                    Investir
                  </Button>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    );
  };

  return (
    <div className="grid gap-5">
      {/* Prêmio de risco do governo */}
      {budget && Number(budget.month.premium) > 0 && <PremiumStrip budget={budget} />}

      {/* CDB de 100% do CDI */}
      {permanentCdb && (
        <Card variant="success">
          <CardContent>
            <div className="flex flex-wrap items-center gap-5">
              <div className="grid min-w-64 flex-1 gap-1">
                <span className="flex flex-wrap items-center gap-2">
                  <DailyLiquidityBadge>Sempre disponível</DailyLiquidityBadge>
                  <b className="text-[15px] font-semibold">{permanentCdb.name}</b>
                  {held.has(permanentCdb.asset_uuid) && (
                    <Badge variant="info" size="sm">
                      na carteira
                    </Badge>
                  )}
                </span>
                <span className="text-[13px] text-muted-foreground">
                  A reserva que rende: {displayRateLabel(permanentCdb.rate_index, permanentCdb.interest_rate)} todo dia
                  útil, e o dinheiro volta ao caixa em qualquer pregão. Fica aberta a partida inteira.
                </span>
              </div>
              <HighlightMetric label="Rentabilidade">
                {displayRateLabel(permanentCdb.rate_index, permanentCdb.interest_rate)}
              </HighlightMetric>
              {showRate && permanentCdb.effective_annual_rate !== null && (
                <HighlightMetric label="Equivale hoje">
                  {displayPercent(permanentCdb.effective_annual_rate)} a.a.
                </HighlightMetric>
              )}
              <HighlightMetric label="IR">
                <Badge variant="secondary">22,5% → {displayPercent(permanentCdb.income_tax_rate_at_maturity, 1)}</Badge>
              </HighlightMetric>
              <Button
                variant="outline"
                size="sm"
                nativeButton={false}
                render={<Link to={`/fixed-income/${permanentCdb.asset_uuid}`} />}
              >
                Investir
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="overflow-hidden">
        {/* Filtros */}
        <CardHeader>
          <div className="flex flex-wrap items-center gap-3">
            <ToggleGroup
              variant="segmented"
              size="field"
              aria-label="Indexador"
              value={[indexFilter]}
              onValueChange={(values) => values[0] && setIndexFilter(values[0] as IndexFilter)}
            >
              {INDEX_FILTERS.map((f) => (
                <ToggleGroupItem key={f.value} value={f.value}>
                  {f.label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            <ToggleGroup
              variant="segmented"
              size="field"
              aria-label="Tipo de título"
              value={[typeFilter]}
              onValueChange={(values) => values[0] && setTypeFilter(values[0] as TypeFilter)}
            >
              {TYPE_FILTERS.map((f) => (
                <ToggleGroupItem key={f.value} value={f.value}>
                  {f.label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            <div className="ml-auto flex items-center gap-3">
              <div className="flex h-10 items-center gap-2 rounded-lg border border-input px-3">
                <Switch id="only-held" checked={onlyHeld} onCheckedChange={setOnlyHeld} />
                <Label htmlFor="only-held">Na carteira · {heldCount}</Label>
              </div>
              <div className="flex h-10 items-center gap-2 rounded-lg border border-input px-3">
                <Switch id="only-daily" checked={onlyDaily} onCheckedChange={setOnlyDaily} />
                <Label htmlFor="only-daily">Só liquidez diária</Label>
              </div>
              <div className="flex h-10 items-center gap-2 rounded-lg border border-input px-3">
                <Switch id="only-exempt" checked={onlyExempt} onCheckedChange={setOnlyExempt} />
                <Label htmlFor="only-exempt">Só isentos de IR</Label>
              </div>
            </div>
          </div>
        </CardHeader>

        {renderBody()}

        {/* Rodapé */}
        <CardFooter>
          <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted-foreground">
            {showRate ? (
              indicators && (
                <span>
                  “Equivale hoje” usa CDI {displayPercent(indicators.cdi)} e IPCA 12m {displayPercent(indicators.ipca)}{" "}
                  do dia simulado (Banco Central). Clique nos cabeçalhos para ordenar.
                </span>
              )
            ) : (
              <span>Modo Especialista: a taxa equivalente fica por sua conta. Clique nos cabeçalhos para ordenar.</span>
            )}
            <span>
              <b className="font-semibold text-success">Qualquer dia</b>: resgata em qualquer pregão pelo valor do dia,
              com o IR do tempo que passou. Acima de 100% do CDI é rara: sai de vez em quando no catálogo do mês, com
              teto por jogador.
            </span>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}

function HighlightMetric({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="grid gap-0.5 border-l border-border pl-5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <b className="font-mono font-semibold whitespace-nowrap">{children}</b>
    </div>
  );
}
