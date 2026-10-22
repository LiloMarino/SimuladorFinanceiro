import { useState } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/shared/components/ui/toggle-group";
import { MetricHint } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import {
  displayDuration,
  displayNumber,
  displayPercent,
} from "@/shared/lib/utils/display";
import {
  countByKind,
  filterRows,
  KIND_FILTERS,
  KIND_LABEL,
  PAGE_SIZE,
  type Kind,
  type KindFilter,
  type Row,
} from "../lib/stats";
import { P95_INFO } from "../lib/p95-info";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";

const KIND_STYLE: Record<Kind, string> = {
  http: "bg-info-soft text-info",
  socket: "bg-purple-100 text-purple-700",
  engine: "bg-success-soft text-success",
};

function KindTag({ kind }: { kind: Kind }) {
  return (
    <span
      className={cn(
        "inline-flex h-5.5 items-center rounded-md px-1.75 text-[11px] font-semibold",
        KIND_STYLE[kind],
      )}
    >
      {KIND_LABEL[kind]}
    </span>
  );
}

/** Fração do tempo medido; abaixo de 1% vira "< 1%". */
function ShareBar({ share }: { share: number }) {
  return (
    <span className="inline-flex items-center justify-end gap-2">
      <span className="inline-block h-1.5 w-24 overflow-hidden rounded-full bg-muted">
        <span
          className="block h-full rounded-full bg-primary"
          style={{ width: `${Math.min(100, share * 100)}%` }}
        />
      </span>
      <span className="w-10 text-right">
        {share > 0 && share < 0.01 ? "< 1%" : displayPercent(share, 0)}
      </span>
    </span>
  );
}

interface TimeTableProps {
  rows: Row[];
  id: string;
}

export function TimeTable({ rows, id }: TimeTableProps) {
  const [kind, setKind] = useState<KindFilter>("all");
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState(false);

  const counts = countByKind(rows);
  const sorting = useTableSort(filterRows(rows, kind, search), {
    kind: (row) => KIND_LABEL[row.kind],
    name: (row) => row.label,
    calls: (row) => row.calls,
    total_ms: (row) => row.total_ms,
    mean_ms: (row) => row.mean_ms,
    p95_ms: (row) => row.p95_ms,
    max_ms: (row) => row.max_ms,
    share: (row) => row.share,
  }, { column: "total_ms", direction: "desc" });
  const filtered = sorting.rows;
  const visible = expanded ? filtered : filtered.slice(0, PAGE_SIZE);

  return (
    <Card id={id}>
      <CardHeader>
        <CardTitle>Tempo gasto por rota ou evento</CardTitle>
        <CardDescription>
          Requisições HTTP, eventos recebidos pelo Socket.IO e o processamento
          de cada dia.
        </CardDescription>
        <CardAction>
          <div className="flex items-center gap-2">
            <ToggleGroup
              variant="segmented"
              aria-label="Filtrar por origem"
              value={[kind]}
              onValueChange={(values) =>
                values[0] && setKind(values[0] as KindFilter)
              }
            >
              {KIND_FILTERS.map((option) => (
                <ToggleGroupItem key={option} value={option}>
                  {option === "all" ? "Tudo" : KIND_LABEL[option]}{" "}
                  {counts[option]}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            <Input
              className="h-9 w-60"
              placeholder="Filtrar por rota ou evento"
              aria-label="Filtrar por rota ou evento"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
        </CardAction>
      </CardHeader>

      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead label="Tipo" {...sorting.header("kind")} className="w-24" />
            <SortableTableHead label="Rota ou evento" {...sorting.header("name")} />
            <SortableTableHead label="Chamadas" numeric {...sorting.header("calls")} />
            <SortableTableHead label="Tempo total" numeric {...sorting.header("total_ms")} />
            <SortableTableHead label="Médio" numeric {...sorting.header("mean_ms")} />
            <SortableTableHead
              label="p95"
              numeric
              {...sorting.header("p95_ms")}
              hint={<MetricHint metric={P95_INFO} />}
            />
            <SortableTableHead label="Máx" numeric {...sorting.header("max_ms")} />
            <SortableTableHead label="Fatia do tempo" numeric {...sorting.header("share")} />
          </TableRow>
        </TableHeader>
        <TableBody>
          {visible.length === 0 && (
            <TableEmptyRow colSpan={8}>
              <span className="text-muted-foreground">
                Nenhuma rota ou evento com esse filtro.
              </span>
            </TableEmptyRow>
          )}
          {visible.map((row) => (
            <TableRow key={`${row.kind}:${row.name}`}>
              <TableCell>
                <KindTag kind={row.kind} />
              </TableCell>
              <TableCell className="max-w-[440px]" title={row.label}>
                <span className="flex items-center font-mono text-[13px]">
                  <span className="truncate">{row.label}</span>
                  {row.flag === "slow" && (
                    <Badge variant="destructive" size="sm" className="ml-2">
                      lenta
                    </Badge>
                  )}
                  {row.flag === "stall" && (
                    <Badge variant="warning" size="sm" className="ml-2">
                      trava às vezes
                    </Badge>
                  )}
                </span>
              </TableCell>
              <TableCell numeric>{displayNumber(row.calls, 0)}</TableCell>
              <TableCell numeric>
                <span className="font-semibold">
                  {displayDuration(row.total_ms)}
                </span>
              </TableCell>
              <TableCell numeric>{displayDuration(row.mean_ms)}</TableCell>
              <TableCell numeric>
                <span
                  className={cn(
                    row.flag === "slow" && "text-destructive",
                    row.flag === "stall" && "text-warning",
                  )}
                >
                  {displayDuration(row.p95_ms)}
                </span>
              </TableCell>
              <TableCell numeric>{displayDuration(row.max_ms)}</TableCell>
              <TableCell numeric>
                <ShareBar share={row.share} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <CardFooter className="justify-between">
        <span className="text-[13px] text-muted-foreground">
          Mostrando {visible.length} de {filtered.length}
        </span>
        {filtered.length > PAGE_SIZE && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setExpanded((open) => !open)}
          >
            {expanded ? "Mostrar menos" : "Mostrar todas"}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
