import { Fragment, useState } from "react";
import { ChevronDown, CircleCheck, Eraser, RefreshCw } from "lucide-react";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
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
import { useTableSort } from "@/shared/hooks/useTableSort";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";
import { useCorrectPriceErrors } from "../hooks/mutations/useCorrectPriceErrors";
import { useRefreshOutdatedStocks } from "../hooks/mutations/useRefreshOutdatedStocks";
import { useRefreshSeries } from "../hooks/mutations/useRefreshSeries";
import { afterEnd } from "../lib/after-end";
import { needsAttention } from "../lib/attention";
import type { TimelineRange } from "../lib/timeline";
import { AssetClassBadge, AssetOriginBadge } from "./asset-badges";
import { ClassifyRow } from "./classify-row";
import { CoverageBar, CoverageDates } from "./coverage-bar";
import { DeleteStockButton } from "./delete-stock-button";
import { SeriesName } from "./series-name";
import { SeriesStatus } from "./series-status";

const COLUMNS = 5;

type Filter = "ALL" | "ATTENTION";

type AssetsTableProps = {
  /** Só as ações, os FIIs, os ETFs, os BDRs e as criptos importados */
  series: SeriesCoverage[];
  range: TimelineRange;
  classifying: string | null;
  onClassify: (key: string | null) => void;
};

/** O que a partida faz depois do último preço do ativo, na linha de baixo da barra. */
function afterEndCaption(item: SeriesCoverage): string | null {
  const after = afterEnd(item);
  if (after === "generated" && item.generated_end) return `Futuro gerado até ${displayIsoDate(item.generated_end)}`;
  if (after === "repeat") return "Depois: repete o último preço";
  return null;
}

/** Os ativos importados, com a classe e a origem trocáveis na própria linha e a situação de cada um. */
export function AssetsTable({ series, range, classifying, onClassify }: AssetsTableProps) {
  const [filter, setFilter] = useState<Filter>("ALL");

  const refreshOne = useRefreshSeries();
  const refreshOutdated = useRefreshOutdatedStocks();
  const correctErrors = useCorrectPriceErrors();

  const outdated = series.filter(isOutdatedStock);
  const attention = series.filter(needsAttention);
  const sorting = useTableSort(filter === "ATTENTION" ? attention : series, {
    asset: (s) => s.key,
    sector: (s) => (s.segment ? `${s.segment.sector} · ${s.segment.segment}` : null),
    end: (s) => s.real_end,
    status: (s) =>
      !s.real_end ? "Sem dado" : isOutdatedStock(s) ? `Parou em ${s.real_end}` : !s.segment ? "Sem setor" : "Em dia",
  });

  const busy = refreshOne.isPending || refreshOutdated.isPending || correctErrors.isPending;
  const updatingThis = (item: SeriesCoverage) => refreshOne.isPending && refreshOne.variables.key === item.key;

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Ativos</CardTitle>
        <CardDescription>
          {series.length} {series.length === 1 ? "ativo" : "ativos"} · importados do yFinance ou de CSV
        </CardDescription>
        <CardAction>
          <div className="flex flex-wrap items-center justify-end gap-2">
            <ToggleGroup
              variant="segmented"
              aria-label="Filtrar ativos"
              value={[filter]}
              onValueChange={(values) => values[0] && setFilter(values[0] as Filter)}
            >
              <ToggleGroupItem value="ALL">Todas</ToggleGroupItem>
              <ToggleGroupItem value="ATTENTION">Precisam de atenção · {attention.length}</ToggleGroupItem>
            </ToggleGroup>
            <Button size="sm" variant="outline" disabled={busy} onClick={() => correctErrors.mutate()}>
              {correctErrors.isPending ? <Spinner /> : <Eraser />}
              Corrigir erros de dado
            </Button>
            <Button
              size="sm"
              disabled={busy || outdated.length === 0}
              onClick={() => refreshOutdated.mutate(outdated.map((s) => s.key))}
            >
              {refreshOutdated.isPending ? <Spinner /> : <RefreshCw />}
              Atualizar desatualizadas ({outdated.length})
            </Button>
          </div>
        </CardAction>
      </CardHeader>

      <Table className="table-fixed">
        <TableHeader>
          <TableRow>
            <SortableTableHead label="Ativo" {...sorting.header("asset")} />
            <SortableTableHead label="Setor · segmento" {...sorting.header("sector")} className="w-[20%]" />
            <SortableTableHead label="Dados reais" {...sorting.header("end")} className="w-[24%]" />
            <SortableTableHead label="Situação" {...sorting.header("status")} className="w-36" />
            <TableHead className="w-24">
              <span className="sr-only">Ações</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {series.length === 0 && (
            <TableEmptyRow colSpan={COLUMNS}>
              <span className="text-muted-foreground">
                Nenhum ativo na base. Importe o primeiro pelo painel ao lado.
              </span>
            </TableEmptyRow>
          )}
          {series.length > 0 && sorting.rows.length === 0 && (
            <TableEmptyRow colSpan={COLUMNS}>
              <div className="grid justify-items-center gap-1.5">
                <CircleCheck className="size-5 text-success" />
                <b className="font-semibold">Nenhuma série precisa de atenção.</b>
                <span className="text-muted-foreground">Tudo em dia, com setor e classe definidos.</span>
              </div>
            </TableEmptyRow>
          )}
          {sorting.rows.map((item) => {
            const stale = isOutdatedStock(item);
            const updating = updatingThis(item);
            const caption = afterEndCaption(item);
            return (
              <Fragment key={item.key}>
                <TableRow variant={updating ? "subtle" : "default"}>
                  {/* Ativo */}
                  <TableCell wrap>
                    <SeriesName series={item} order="code-first">
                      <div className="mt-1.5 flex flex-wrap gap-1.5">
                        {item.asset_class && <AssetClassBadge ticker={item.key} value={item.asset_class} />}
                        {item.origin && <AssetOriginBadge ticker={item.key} value={item.origin} />}
                      </div>
                    </SeriesName>
                  </TableCell>

                  {/* Setor · segmento */}
                  <TableCell wrap>
                    {item.segment ? (
                      <button
                        type="button"
                        onClick={() => onClassify(item.key)}
                        className="flex max-w-full items-start gap-1.5 text-left"
                        aria-label={`Trocar o setor de ${item.key}`}
                      >
                        <span className="grid min-w-0 gap-0.5">
                          <span className="text-[13px] leading-snug">{item.segment.sector}</span>
                          <span className="text-xs leading-snug text-muted-foreground">{item.segment.segment}</span>
                        </span>
                        <ChevronDown className="mt-0.5 size-3.5 shrink-0 text-faint-foreground" />
                      </button>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => onClassify(item.key)}>
                        Classificar
                      </Button>
                    )}
                  </TableCell>

                  {/* Dados reais */}
                  <TableCell>
                    <div className="grid gap-1.5">
                      <CoverageDates series={item} />
                      <CoverageBar series={item} range={range} />
                      {caption && <span className="text-xs text-muted-foreground">{caption}</span>}
                    </div>
                  </TableCell>

                  {/* Situação */}
                  <TableCell>
                    <SeriesStatus series={item} updating={updating} />
                  </TableCell>

                  {/* Ações: toda linha atualiza e exclui; só a desatualizada destaca o atualizar */}
                  <TableCell>
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant={stale ? "outline" : "ghost"}
                        size="icon-sm"
                        aria-label={`Atualizar ${item.key}`}
                        title={`Atualizar ${item.key}`}
                        disabled={busy}
                        onClick={() => refreshOne.mutate(item)}
                      >
                        {updating ? <Spinner /> : <RefreshCw />}
                      </Button>
                      <DeleteStockButton stock={item} disabled={busy} />
                    </div>
                  </TableCell>
                </TableRow>

                {classifying === item.key && (
                  <ClassifyRow series={item} columns={COLUMNS} onClose={() => onClassify(null)} />
                )}
              </Fragment>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
