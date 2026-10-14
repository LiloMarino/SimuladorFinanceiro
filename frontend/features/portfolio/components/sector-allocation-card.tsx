import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { displayMoney, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";

const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"];
const OTHERS_COLOR = "var(--input)";

/** Renda variável por setor: uma barra só e a lista setor · segmento. */
export function SectorAllocationCard({ portfolio }: { portfolio: PortfolioState }) {
  const sectors = portfolio.sectors;
  const colorOf = (index: number, sector: string | null) =>
    sector === null || index >= COLORS.length ? OTHERS_COLOR : COLORS[index];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Renda variável por setor</CardTitle>
        <CardDescription>
          Onde está o dinheiro em ações. A classificação se edita na Central de dados, fora da partida.
        </CardDescription>
        {portfolio.effective_sectors && (
          <CardAction>
            <Badge variant="secondary">
              {sectors.length} {sectors.length === 1 ? "setor" : "setores"} · diversificação{" "}
              {displayNumber(portfolio.effective_sectors, 2)}
            </Badge>
          </CardAction>
        )}
      </CardHeader>
      <CardContent>
        {sectors.length === 0 ? (
          <p className="py-6 text-center text-[13px] text-muted-foreground">Nenhuma ação na carteira ainda.</p>
        ) : (
          <div className="grid gap-4">
            <div className="flex h-3.5 gap-0.5 overflow-hidden rounded-full">
              {sectors.map((s, i) => (
                <span
                  key={s.sector ?? "none"}
                  style={{ width: `${Number(s.fraction) * 100}%`, backgroundColor: colorOf(i, s.sector) }}
                  title={`${s.sector ?? "Sem setor"} · ${displayPercent(s.fraction)}`}
                />
              ))}
            </div>
            <ul className="grid gap-2.5 text-[13px]">
              {sectors.map((s, i) => (
                <li key={s.sector ?? "none"} className="grid gap-1">
                  <div className="flex items-center gap-2">
                    <span
                      className="size-2.5 rounded-sm"
                      style={{ backgroundColor: colorOf(i, s.sector) }}
                      aria-hidden="true"
                    />
                    <span className="flex-1 font-medium">{s.sector ?? "Sem setor"}</span>
                    <span className="font-mono">{displayMoney(s.value)}</span>
                    <span className="w-16 text-right font-mono text-muted-foreground">
                      {displayPercent(s.fraction)}
                    </span>
                  </div>
                  {s.segments.map((seg) => (
                    <div
                      key={seg.segment ?? "none"}
                      className="flex items-center gap-2 pl-4.5 text-xs text-muted-foreground"
                    >
                      <span className="flex-1">{seg.segment ?? "Sem segmento"}</span>
                      <span className="font-mono">{displayMoney(seg.value)}</span>
                      <span className="w-16 text-right font-mono">{displayPercent(seg.fraction)}</span>
                    </div>
                  ))}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
