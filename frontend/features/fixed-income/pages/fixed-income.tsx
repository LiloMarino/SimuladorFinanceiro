import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardFooter, CardHeader } from "@/shared/components/ui/card";
import { Empty, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
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
import { ErrorState } from "@/shared/components/error-state";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useEconomicIndicators } from "@/shared/hooks/queries/useEconomicIndicators";
import { displayDate, displayPercent, displayRateLabel, parseLocalDate } from "@/shared/lib/utils/display";
import type { FixedIncomeOffer } from "@/types";
import { useFixedIncomeAssets } from "../hooks/queries/useFixedIncomeAssets";
import { INVESTMENT_TYPE_LABELS, timeToMaturity } from "../lib/labels";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber } from "@/shared/lib/table-sort";

// Com a taxa equivalente escondida a tabela perde a coluna "Equivale hoje"
const COLUMNS = 7;
const COLUMNS_WITHOUT_RATE = 6;

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
  const { data: offers, isLoading, error, refetch } = useFixedIncomeAssets();
  const { data: portfolio } = usePortfolio();
  const { data: simulation } = useSimulationState();
  const { data: indicators } = useEconomicIndicators();
  const showRate = useSimulation().simulation?.simulation?.show_equivalent_rate ?? true;
  const [indexFilter, setIndexFilter] = useState<IndexFilter>("ALL");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("ALL");
  const [onlyExempt, setOnlyExempt] = useState(false);

  const held = new Set((portfolio?.fixed_income ?? []).map((p) => p.asset.asset_uuid));
  const filtered = (offers ?? [])
    .filter((o) => (indexFilter === "ALL" || o.rate_index === indexFilter) && matchesType(o, typeFilter))
    .filter((o) => !onlyExempt || o.tax_exempt);
  const sorting = useTableSort(filtered, {
    name: o => o.name, type: o => INVESTMENT_TYPE_LABELS[o.investment_type],
    rate: o => Number(o.interest_rate), equivalent: o => sortNumber(o.effective_annual_rate),
    maturity: o => o.maturity_date, tax: o => o.tax_exempt ? 0 : Number(o.income_tax_rate_at_maturity),
  }, showRate ? { column: "equivalent", direction: "desc" } : { column: "maturity", direction: "asc" });
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
        <EmptyTitle>{offers?.length ? "Nenhum título com esse filtro" : "Nenhum título disponível nesta partida"}</EmptyTitle>
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
          {visible.map((o) => (
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
                  <span className="max-w-[300px] truncate text-xs text-muted-foreground">{o.issuer}</span>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="secondary">{INVESTMENT_TYPE_LABELS[o.investment_type]}</Badge>
              </TableCell>
              <TableCell>
                <span className="font-mono">{displayRateLabel(o.rate_index, o.interest_rate)}</span>
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
                    <span className="font-mono font-semibold">{o.effective_annual_rate === null ? "—" : `${displayPercent(o.effective_annual_rate)} a.a.`}</span>
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
          ))}
        </TableBody>
      </Table>
    );
  };

  return (
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
          <div className="ml-auto flex h-10 items-center gap-2 rounded-lg border border-input px-3">
            <Switch id="only-exempt" checked={onlyExempt} onCheckedChange={setOnlyExempt} />
            <Label htmlFor="only-exempt">Só isentos de IR</Label>
          </div>
        </div>
      </CardHeader>

      {renderBody()}

      {showRate ? (
        indicators && (
          <CardFooter>
            <span className="text-xs text-muted-foreground">
              “Equivale hoje” usa CDI {displayPercent(indicators.cdi)} e IPCA 12m {displayPercent(indicators.ipca)} do
              dia simulado (Banco Central). Clique nos cabeçalhos para ordenar.
            </span>
          </CardFooter>
        )
      ) : (
        <CardFooter>
          <span className="text-xs text-muted-foreground">
            Modo Especialista: a taxa equivalente fica por sua conta. Clique nos cabeçalhos para ordenar.
          </span>
        </CardFooter>
      )}
    </Card>
  );
}
