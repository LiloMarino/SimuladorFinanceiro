import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  Rectangle,
  type RectangleProps,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { CHART_TICK } from "@/shared/lib/chart-text";
import { displayMonthShort, displayMoney, displayNumber } from "@/shared/lib/utils/display";
import type { StateCompanyMonth } from "@/types";

type MonthRow = {
  month: string;
  label: string;
  price: number | null;
  fairValue: number | null;
  profit: number | null;
  dividend: number | null;
};

const toNumber = (value: string | null) => (value === null ? null : Number(value));

function toRows(months: StateCompanyMonth[]): MonthRow[] {
  return months.map((item) => ({
    month: item.month,
    label: displayMonthShort(item.month),
    price: toNumber(item.price),
    fairValue: toNumber(item.fair_value),
    profit: toNumber(item.profit),
    dividend: toNumber(item.dividend),
  }));
}

function Legend({ items }: { items: { color: string; label: string }[] }) {
  return (
    <div className="flex flex-wrap gap-4">
      {items.map((item) => (
        <span key={item.label} className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
          <i className={`size-2.5 rounded-[3px] ${item.color}`} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

const MONEY_AXIS = {
  tick: CHART_TICK,
  axisLine: false,
  tickLine: false,
  width: 44,
  tickFormatter: (value: number) => displayNumber(value, 0),
} as const;

/** O preço no fim de cada mês contra o valor justo, em reais por ação. */
function PriceChart({ rows }: { rows: MonthRow[] }) {
  return (
    <div className="grid gap-2">
      <p className="text-xs text-muted-foreground">Preço e valor justo, em reais por ação</p>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis dataKey="label" tick={CHART_TICK} axisLine={false} tickLine={false} />
          <YAxis domain={["auto", "auto"]} {...MONEY_AXIS} />
          <Tooltip
            cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
            content={({ active, payload }) => {
              const row = payload[0]?.payload as MonthRow | undefined;
              if (!active || !row) return null;
              return (
                <div className="grid gap-0.5 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                  <span className="text-muted-foreground">{row.label}</span>
                  <span className="font-mono font-semibold">
                    Preço: {row.price === null ? "sem negócio" : displayMoney(row.price)}
                  </span>
                  <span className="font-mono text-muted-foreground">
                    Valor justo: {row.fairValue === null ? "—" : displayMoney(row.fairValue)}
                  </span>
                </div>
              );
            }}
          />
          <Line
            dataKey="fairValue"
            type="linear"
            stroke="var(--expansion-government)"
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={false}
            connectNulls
            isAnimationActive={false}
          />
          <Line
            dataKey="price"
            type="linear"
            stroke="var(--chart-1)"
            strokeWidth={2}
            dot={false}
            connectNulls
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <Legend
        items={[
          { color: "bg-chart-1", label: "Preço no fim do mês" },
          { color: "bg-expansion-government", label: "Valor justo (tracejado)" },
        ]}
      />
    </div>
  );
}

/** O lucro e o dividendo de cada mês, em reais por ação; o mês de prejuízo fica em vermelho. */
function ProfitChart({ rows }: { rows: MonthRow[] }) {
  return (
    <div className="grid gap-2">
      <p className="text-xs text-muted-foreground">Lucro e dividendo, em reais por ação</p>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis dataKey="label" tick={CHART_TICK} axisLine={false} tickLine={false} />
          <YAxis {...MONEY_AXIS} />
          <Tooltip
            cursor={{ fill: "var(--muted)", fillOpacity: 0.6 }}
            content={({ active, payload }) => {
              const row = payload[0]?.payload as MonthRow | undefined;
              if (!active || !row) return null;
              const loss = row.profit !== null && row.profit < 0;
              return (
                <div className="grid gap-0.5 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                  <span className="text-muted-foreground">{row.label}</span>
                  <span className={loss ? "font-mono font-semibold text-destructive" : "font-mono font-semibold"}>
                    Lucro: {row.profit === null ? "—" : displayMoney(row.profit)}
                    {loss && " (prejuízo)"}
                  </span>
                  <span className="font-mono text-muted-foreground">
                    Dividendo: {row.dividend === null ? "—" : displayMoney(row.dividend)}
                  </span>
                </div>
              );
            }}
          />
          {/* Lucro: a barra de um mês de prejuízo sai em vermelho */}
          <Bar
            dataKey="profit"
            isAnimationActive={false}
            shape={(props: RectangleProps & { payload?: MonthRow }) => (
              <Rectangle
                {...props}
                radius={[3, 3, 0, 0]}
                fill={
                  props.payload?.profit != null && props.payload.profit < 0 ? "var(--destructive)" : "var(--chart-9)"
                }
              />
            )}
          />
          <Bar dataKey="dividend" fill="var(--chart-1)" radius={[3, 3, 0, 0]} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
      <Legend
        items={[
          { color: "bg-chart-9", label: "Lucro por ação" },
          { color: "bg-chart-1", label: "Dividendo por ação" },
          { color: "bg-destructive", label: "Mês de prejuízo" },
        ]}
      />
    </div>
  );
}

/** Preço, lucro e dividendo mês a mês; o gráfico começa quando há dois meses para ligar. */
export function StateCompanyChartCard({ months }: { months: StateCompanyMonth[] }) {
  const rows = toRows(months);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Preço, lucro e dividendo por mês</CardTitle>
        <CardDescription>
          Quando o preço fica abaixo do valor justo, a ação está barata pelo lucro que se espera dela.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {rows.length < 2 ? (
          <p className="py-10 text-center text-[13px] text-muted-foreground">
            Os gráficos aparecem depois dos primeiros meses fechados da estatal.
          </p>
        ) : (
          <div className="grid gap-5">
            <PriceChart rows={rows} />
            <ProfitChart rows={rows} />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
