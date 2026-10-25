import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Progress } from "@/shared/components/ui/progress";
import { displayMoney, displayPercent, displayPercentagePoints } from "@/shared/lib/utils/display";
import type { StrategyAllocation } from "@/types";

type AllocationBlockProps = {
  allocation: StrategyAllocation;
};

/** A carteira da estratégia, lado a lado contra a meta, e o que ela faria hoje. */
export function AllocationBlock({ allocation }: AllocationBlockProps) {
  return (
    <div className="grid gap-3.5">
      <div className="grid gap-4">
        {allocation.items.map((item) => {
          const deviation = Number(item.deviation_pp);
          const outside = Math.abs(deviation) > allocation.limit_pp;
          return (
            <div key={item.label} className="grid gap-1.5">
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm font-medium">{item.label}</span>
                <span className="flex items-center gap-2">
                  <span className="font-mono text-sm">{displayMoney(item.value)}</span>
                  <Badge variant={outside ? "warning" : "secondary"} size="tag" numeric>
                    {displayPercentagePoints(deviation / 100, 1)}
                  </Badge>
                </span>
              </div>
              <Bar label="Atual" percent={Number(item.current_pct)} tone="default" />
              <Bar label="Meta" percent={Number(item.target_pct)} tone="soft" />
            </div>
          );
        })}
      </div>

      <p className="flex items-start gap-1.5 text-xs text-muted-foreground">
        <span>
          Limite de desvio: {allocation.limit_pp} p.p. Dentro dele, o caixa parado vai para o lado mais abaixo da meta;
          fora, ela vende ou resgata para voltar.
        </span>
        <InfoHint label="O que é p.p.">
          p.p. é a diferença entre dois percentuais: 66% de ações contra a meta de 60% são 6 p.p. acima. Com limite de 5
          p.p., esse desvio já faria a estratégia vender.
        </InfoHint>
      </p>

      {!allocation.has_liquid_offer && (
        <p className="text-xs text-warning">
          Não há renda fixa de liquidez diária à venda hoje: só o lado das ações opera.
        </p>
      )}

      <div className="grid gap-1 rounded-lg bg-subtle px-2.5 py-2 text-xs">
        <span className="font-medium">O que ela faria hoje</span>
        {allocation.today.length > 0 ? (
          <ul className="grid gap-0.5 text-muted-foreground">
            {allocation.today.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        ) : (
          <span className="text-muted-foreground">Nada: a carteira está dentro do limite e não há caixa parado.</span>
        )}
      </div>
    </div>
  );
}

type BarProps = {
  label: string;
  /** Percentual de 0 a 100 */
  percent: number;
  tone: "default" | "soft";
};

function Bar({ label, percent, tone }: BarProps) {
  return (
    <div className="grid grid-cols-[44px_minmax(0,1fr)_52px] items-center gap-x-3">
      <span className="text-[11px] text-faint-foreground">{label}</span>
      <Progress value={percent} size="md" indicatorTone={tone} aria-label={`${label}: ${percent}%`} />
      <span className="text-right font-mono text-xs text-muted-foreground">{displayPercent(percent / 100, 1)}</span>
    </div>
  );
}
