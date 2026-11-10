import { Card, CardContent } from "@/shared/components/ui/card";
import { Kpi } from "@/shared/components/kpi";
import { MetricLabel } from "@/shared/components/metric-hint";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { Presidency } from "@/types";
import { LEGACY, PRESIDENT_SALARY } from "../lib/government-metrics";
import { salariesLabel } from "../lib/presidency";

type PresidencyPayCardProps = { presidency: Presidency };

/** O que o cargo paga: o salário mensal, o legado que a aprovação acumula e o que o último mês somou. */
export function PresidencyPayCard({ presidency }: PresidencyPayCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <h2 className="text-[15px] font-semibold">O que a presidência paga</h2>

          <div className="grid grid-cols-3 gap-4">
            <Kpi
              label={<MetricLabel metric={PRESIDENT_SALARY} />}
              value={displayMoneyWhole(presidency.monthly_salary)}
              note={`${Number(presidency.salary_multiple)}× o salário da partida`}
            />
            <Kpi
              label={<MetricLabel metric={LEGACY} />}
              value={displayMoneyWhole(presidency.legacy_amount)}
              note={salariesLabel(presidency.legacy_salaries)}
            />
            <Kpi
              label="Último mês"
              value={salariesLabel(presidency.last_month_salaries)}
              note={`Aprovação acima de ${presidency.legacy_floor} soma`}
            />
          </div>

          <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
            O legado é pago quando o presidente deixa o cargo no fim do mandato. No impeachment, o legado todo se perde.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
