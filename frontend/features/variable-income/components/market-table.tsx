import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { displayCompactNumber, displayMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { MarketQuote } from "@/types";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";

const COLUMNS = 7;

const CLASS_LABELS: Record<MarketQuote["asset_class"], string | null> = {
  STOCK: null,
  FII: "FII",
  ETF: "ETF",
  BDR: "BDR",
};

/** Onde o fechamento ficou entre a mínima e a máxima do dia. */
function DayRange({ quote }: { quote: MarketQuote }) {
  const span = quote.high - quote.low;
  const position = span > 0 ? ((quote.close - quote.low) / span) * 100 : 50;
  return (
    <div className="grid w-32 gap-1">
      <div className="relative h-1.5 rounded-full bg-muted">
        <span className="absolute -top-0.5 h-2.5 w-0.5 rounded-full bg-foreground" style={{ left: `${position}%` }} />
      </div>
      <div className="flex justify-between font-mono text-[11px] text-faint-foreground">
        <span>{displayMoney(quote.low)}</span>
        <span>{displayMoney(quote.high)}</span>
      </div>
    </div>
  );
}

/** Mini gráfico dos últimos 30 fechamentos; a cor diz se subiu ou caiu no período. */
function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2) return <span className="text-faint-foreground">—</span>;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const points = values
    .map((v, i) => `${((i / (values.length - 1)) * 96).toFixed(1)},${(24 - ((v - min) / span) * 22).toFixed(1)}`)
    .join(" ");
  const up = values.at(-1)! >= values[0];
  return (
    <svg
      viewBox="0 0 96 26"
      className="h-[26px] w-24"
      role="img"
      aria-label={up ? "Subiu em 30 dias" : "Caiu em 30 dias"}
    >
      <polyline points={points} fill="none" stroke={up ? "var(--success)" : "var(--destructive)"} strokeWidth="1.5" />
    </svg>
  );
}

type MarketTableProps = {
  quotes: MarketQuote[];
  holdings: Map<string, number>;
  /** Erro, base vazia ou filtro sem resultado: ocupa uma linha, com o cabeçalho mantido */
  message: ReactNode;
};

export function MarketTable({ quotes, holdings, message }: MarketTableProps) {
  const navigate = useNavigate();
  const sorting = useTableSort(quotes, {
    ticker: q => q.ticker, price: q => q.close, day: q => q.change_pct,
    range: q => q.high - q.low,
    month: q => q.sparkline.length > 1 && q.sparkline[0] !== 0 ? q.sparkline.at(-1)! / q.sparkline[0] - 1 : null,
    volume: q => q.volume, held: q => holdings.get(q.ticker) ?? 0,
  });

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <SortableTableHead {...sorting.header("ticker")} label="Ativo" />
          <SortableTableHead {...sorting.header("price")} label="Preço" numeric />
          <SortableTableHead {...sorting.header("day")} label="Dia" numeric />
          <SortableTableHead {...sorting.header("range")} label="Faixa do dia" hint={<span className="sr-only">Amplitude entre mínima e máxima</span>} />
          <SortableTableHead {...sorting.header("month")} label="30 dias" />
          <SortableTableHead {...sorting.header("volume")} label="Volume" numeric />
          <SortableTableHead {...sorting.header("held")} label="Você tem" numeric />
        </TableRow>
      </TableHeader>
      <TableBody>
        {message && <TableEmptyRow colSpan={COLUMNS}>{message}</TableEmptyRow>}
        {sorting.rows.map((q) => {
          const held = holdings.get(q.ticker);
          const classLabel = CLASS_LABELS[q.asset_class];
          return (
            <TableRow key={q.ticker} onActivate={() => void navigate(`/variable-income/${q.ticker}`)}>
              <TableCell>
                <div className="grid">
                  <span className="flex items-center gap-2">
                    <span className="font-mono font-semibold">{q.ticker}</span>
                    {classLabel && (
                      <Badge variant="secondary" size="sm">
                        {classLabel}
                      </Badge>
                    )}
                  </span>
                  <span className="max-w-56 truncate text-xs text-muted-foreground">{q.name}</span>
                </div>
              </TableCell>
              <TableCell numeric>
                <span className="font-semibold">{displayMoney(q.close)}</span>
              </TableCell>
              <TableCell numeric>
                <Badge variant={q.change_pct >= 0 ? "success" : "destructive"}>
                  {displaySignedPercent(q.change_pct)}
                </Badge>
              </TableCell>
              <TableCell>
                <DayRange quote={q} />
              </TableCell>
              <TableCell>
                <Sparkline values={q.sparkline} />
              </TableCell>
              <TableCell numeric>{displayCompactNumber(q.volume)}</TableCell>
              <TableCell numeric>
                {held ? (
                  <Badge variant="info">
                    {held} {held === 1 ? "ação" : "ações"}
                  </Badge>
                ) : (
                  <span className="text-faint-foreground">—</span>
                )}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
