import { Card, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { MetricHint } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { displayBytes, displayDuration, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { MetricsData, TrafficItem } from "@/types";
import { isHeavy } from "../lib/stats";
import {
  QUEUE_INFO,
  RATE_INFO,
  SENDS_INFO,
  SIZE_P95_INFO,
  TOTAL_INFO,
  TYPICAL_INFO,
  UNHEARD_INFO,
  VOLUME_INFO,
} from "../lib/traffic-info";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";

interface TrafficTableProps {
  traffic: TrafficItem[];
  windowSeconds: MetricsData["traffic_window_s"];
}

const optionalBytes = (bytes: number | null) => (bytes === null ? "—" : displayBytes(bytes));

/** Envios sem destinatário e a fração deles; a base do percentual é a coluna Envios, ao lado. */
function Unheard({ item }: { item: TrafficItem }) {
  if (item.unheard === 0) return <span className="text-muted-foreground">0</span>;
  return (
    <span>
      {displayNumber(item.unheard, 0)}
      <span className="text-muted-foreground"> · {displayPercent(item.unheard / item.sends, 0)}</span>
    </span>
  );
}

/** O que o servidor envia a cada jogador: o agora vem da janela recente, o resto fica até zerar. */
export function TrafficTable({ traffic, windowSeconds }: TrafficTableProps) {
  const sorting = useTableSort(
    traffic,
    {
      event: (item) => item.event,
      rate: (item) => item.msgs_per_s,
      volume: (item) => item.bytes_per_s,
      sends: (item) => item.sends,
      unheard: (item) => item.unheard,
      total: (item) => item.total_bytes,
      typical: (item) => item.typical_bytes,
      p95: (item) => item.p95_bytes,
      queue: (item) => item.queue_p95_ms,
      last: (item) => item.last_sent_at,
    },
    { column: "total", direction: "desc" },
  );
  const windowLabel = displayNumber(windowSeconds, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>O que vai para o navegador</CardTitle>
        <CardDescription>
          Mensagens que o servidor envia a cada jogador. “Agora” cobre os últimos {windowLabel} s e zera com a partida
          pausada; o resto se acumula até você zerar as medições.
        </CardDescription>
      </CardHeader>
      <Table>
        <TableHeader>
          {/* Grupos de colunas */}
          <TableRow>
            <TableHead />
            <TableHead colSpan={2}>Agora · últimos {windowLabel} s</TableHead>
            <TableHead colSpan={7}>Desde que zerou</TableHead>
          </TableRow>
          <TableRow>
            <SortableTableHead label="Evento" {...sorting.header("event")} />
            <SortableTableHead
              label="Msg/s"
              numeric
              {...sorting.header("rate")}
              hint={<MetricHint metric={RATE_INFO} />}
            />
            <SortableTableHead
              label="Volume"
              numeric
              {...sorting.header("volume")}
              hint={<MetricHint metric={VOLUME_INFO} />}
            />
            <SortableTableHead
              label="Envios"
              numeric
              {...sorting.header("sends")}
              hint={<MetricHint metric={SENDS_INFO} />}
            />
            <SortableTableHead
              label="Sem ninguém"
              numeric
              {...sorting.header("unheard")}
              hint={<MetricHint metric={UNHEARD_INFO} />}
            />
            <SortableTableHead
              label="Total"
              numeric
              {...sorting.header("total")}
              hint={<MetricHint metric={TOTAL_INFO} />}
            />
            <SortableTableHead
              label="Típico"
              numeric
              {...sorting.header("typical")}
              hint={<MetricHint metric={TYPICAL_INFO} />}
            />
            <SortableTableHead
              label="p95"
              numeric
              {...sorting.header("p95")}
              hint={<MetricHint metric={SIZE_P95_INFO} />}
            />
            <SortableTableHead
              label="Atraso p95"
              numeric
              {...sorting.header("queue")}
              hint={<MetricHint metric={QUEUE_INFO} />}
            />
            <SortableTableHead label="Último" numeric {...sorting.header("last")} />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorting.rows.length === 0 && (
            <TableEmptyRow colSpan={10}>
              <span className="text-muted-foreground">Nada enviado desde que zerou.</span>
            </TableEmptyRow>
          )}
          {sorting.rows.map((item) => {
            const idle = item.msgs_per_s === 0;
            return (
              <TableRow key={item.event}>
                <TableCell>
                  <span className="font-mono text-[13px]">{item.event}</span>
                </TableCell>
                <TableCell numeric>
                  {idle ? "—" : displayNumber(item.msgs_per_s, item.msgs_per_s < 10 ? 1 : 0)}
                </TableCell>
                <TableCell numeric>{idle ? "—" : `${displayBytes(item.bytes_per_s)}/s`}</TableCell>
                <TableCell numeric>{displayNumber(item.sends, 0)}</TableCell>
                <TableCell numeric>
                  <Unheard item={item} />
                </TableCell>
                <TableCell numeric>
                  <span className="font-semibold">{displayBytes(item.total_bytes)}</span>
                </TableCell>
                <TableCell numeric>
                  <span className={cn(isHeavy(item) && "text-warning")}>{optionalBytes(item.typical_bytes)}</span>
                </TableCell>
                <TableCell numeric>{optionalBytes(item.p95_bytes)}</TableCell>
                <TableCell numeric>{item.queue_p95_ms === null ? "—" : displayDuration(item.queue_p95_ms)}</TableCell>
                <TableCell numeric>
                  {item.last_sent_at === null ? "—" : new Date(item.last_sent_at).toLocaleTimeString("pt-BR")}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
