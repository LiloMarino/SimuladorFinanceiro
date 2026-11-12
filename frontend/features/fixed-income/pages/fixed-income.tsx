import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Landmark } from "lucide-react";
import { Card, CardFooter, CardHeader } from "@/shared/components/ui/card";
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
import { ErrorState } from "@/shared/components/error-state";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useEconomicIndicators } from "@/shared/hooks/queries/useEconomicIndicators";
import { displayPercent } from "@/shared/lib/utils/display";
import type { FixedIncomeOffer } from "@/types";
import { useFixedIncomeAssets } from "../hooks/queries/useFixedIncomeAssets";
import { OfferRow, PinnedOfferRow } from "../components/offer-row";
import { isDollarAccount, isPermanentCdb } from "../lib/daily-liquidity";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber } from "@/shared/lib/table-sort";

// Com a taxa equivalente escondida a tabela perde a coluna "Equivale hoje"
const COLUMNS = 7;
const COLUMNS_WITHOUT_RATE = 6;

type IndexFilter = "ALL" | FixedIncomeOffer["rate_index"];
type TypeFilter = "ALL" | "CDB" | "LCI_LCA";

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
];

const matchesType = (o: FixedIncomeOffer, filter: TypeFilter) =>
  filter === "ALL" ||
  (filter === "LCI_LCA" ? o.investment_type === "LCI" || o.investment_type === "LCA" : o.investment_type === filter);

export default function FixedIncomePage() {
  const [searchParams] = useSearchParams();
  const { data: offers, isLoading, error, refetch } = useFixedIncomeAssets();
  const { data: portfolio } = usePortfolio();
  const { data: simulation } = useSimulationState();
  const { data: indicators } = useEconomicIndicators();
  const { simulation: match } = useSimulation();
  const showRate = match?.simulation?.show_equivalent_rate ?? true;
  const [indexFilter, setIndexFilter] = useState<IndexFilter>("ALL");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("ALL");
  const [onlyExempt, setOnlyExempt] = useState(false);
  const [onlyHeld, setOnlyHeld] = useState(false);
  // O detalhe de um título sem liquidez aponta para cá com o filtro já ligado
  const [onlyDaily, setOnlyDaily] = useState(searchParams.get("liquidity") === "daily");

  const held = new Map((portfolio?.fixed_income ?? []).map((p) => [p.asset.asset_uuid, p]));
  // O CDB de 100% do CDI e a conta em dólar abrem a tabela, fixos em qualquer ordenação
  const pinned = (offers ?? []).filter((o) => isPermanentCdb(o) || isDollarAccount(o));
  const listed = (offers ?? []).filter((o) => !pinned.includes(o));
  const heldCount = (offers ?? []).filter((o) => held.has(o.asset_uuid)).length;
  const passesFilters = (o: FixedIncomeOffer) =>
    (!onlyHeld || held.has(o.asset_uuid)) &&
    (indexFilter === "ALL" || o.rate_index === indexFilter) &&
    matchesType(o, typeFilter) &&
    (!onlyExempt || o.tax_exempt) &&
    (!onlyDaily || o.daily_liquidity);
  const visiblePinned = pinned.filter(passesFilters);
  const filtered = listed.filter(passesFilters);
  const sorting = useTableSort(
    filtered,
    {
      name: (o) => o.name,
      rate: (o) => Number(o.interest_rate),
      equivalent: (o) => sortNumber(o.effective_annual_rate),
      maturity: (o) => o.maturity_date,
      liquidity: (o) => (o.daily_liquidity ? 0 : 1),
      tax: (o) => (o.tax_exempt ? 0 : Number(o.income_tax_rate_at_maturity)),
    },
    showRate ? { column: "equivalent", direction: "desc" } : { column: "maturity", direction: "asc" },
  );
  const visible = sorting.rows;
  const topRate = Math.max(...[...visiblePinned, ...visible].map((o) => Number(o.effective_annual_rate)), 0.0001);
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
        {onlyDaily && visiblePinned.length > 0 ? (
          <>
            <EmptyTitle>Nenhuma oferta acima de 100% do CDI com liquidez diária este mês</EmptyTitle>
            <EmptyDescription>As ofertas de “Sempre disponíveis”, no topo, seguem abertas.</EmptyDescription>
          </>
        ) : onlyHeld && heldCount === 0 ? (
          <>
            <EmptyTitle>Nenhum título da lista na carteira</EmptyTitle>
            <EmptyDescription>Os títulos que você comprar aparecem aqui.</EmptyDescription>
          </>
        ) : onlyHeld && visiblePinned.length > 0 ? (
          <EmptyTitle>Nenhuma oferta do mês na carteira</EmptyTitle>
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
    const columns = showRate ? COLUMNS : COLUMNS_WITHOUT_RATE;
    // Os cabeçalhos de grupo só existem quando há linhas fixas para separar das ofertas
    const grouped = visiblePinned.length > 0;
    return (
      <Table>
        {header}
        <TableBody>
          {grouped && (
            <TableRow variant="group">
              <TableCell variant="group" colSpan={columns}>
                <span className="tracking-wider uppercase">Sempre disponíveis</span>
                <span className="ml-2 font-normal text-muted-foreground">
                  abertas a partida inteira, ficam no topo em qualquer ordenação
                </span>
              </TableCell>
            </TableRow>
          )}
          {visiblePinned.map((o) => (
            <PinnedOfferRow
              key={o.asset_uuid}
              offer={o}
              position={held.get(o.asset_uuid)}
              showApplied={onlyHeld}
              showRate={showRate}
              topRate={topRate}
            />
          ))}
          {grouped && (
            <TableRow variant="group">
              <TableCell variant="group" colSpan={columns}>
                <span className="tracking-wider uppercase">Ofertas do mês</span>
                <span className="ml-2 font-normal text-muted-foreground">mudam com o catálogo de cada mês</span>
              </TableCell>
            </TableRow>
          )}
          {message && <TableEmptyRow colSpan={columns}>{message}</TableEmptyRow>}
          {visible.map((o) => (
            <OfferRow
              key={o.asset_uuid}
              offer={o}
              position={held.get(o.asset_uuid)}
              showApplied={onlyHeld}
              showRate={showRate}
              topRate={topRate}
              today={today}
            />
          ))}
        </TableBody>
      </Table>
    );
  };

  return (
    <div className="grid gap-5">
      {/* Aviso: os títulos do governo moram no Tesouro */}
      <div className="flex items-center gap-2 text-[13px] text-muted-foreground">
        <Landmark className="size-4" />
        <span>
          Selic, Prefixado e IPCA+ estão no{" "}
          <Link to="/treasury" className="font-medium text-primary hover:text-primary-hover">
            Tesouro →
          </Link>
        </span>
      </div>

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
