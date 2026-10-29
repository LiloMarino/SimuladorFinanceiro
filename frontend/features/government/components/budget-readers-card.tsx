import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import type { GovernmentApproval } from "@/types";
import { factorPoints } from "../lib/approval";
import { budgetFactors } from "../lib/budget";
import { GROUP_INFO, READING_LABEL } from "../lib/voters";

type BudgetReadersCardProps = { approval: GovernmentApproval };

/** Quem lê a conta: o desemprego e o prêmio de risco que cada grupo de eleitores lê, e quanto cada um empurra a satisfação dele. */
export function BudgetReadersCard({ approval }: BudgetReadersCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 gap-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-[15px] font-semibold">Quem lê a conta</h2>
            <span className="text-xs text-muted-foreground">
              Cada grupo de eleitores lê o desemprego e o prêmio de risco; o efeito entra no alvo de satisfação dele, em
              pontos.
            </span>
          </div>
          <div className="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-3">
            {approval.groups.map((group) => {
              const factors = budgetFactors(group);
              const reads = factors.map((factor) => READING_LABEL[factor.kind]);
              return (
                <div key={group.group} className="grid content-start gap-1 rounded-lg border bg-subtle p-3">
                  <b className="text-[13px]">{GROUP_INFO[group.group].short}</b>
                  <span className="text-xs text-muted-foreground">lê: {reads.join(" e ")}</span>
                  {factors.map((factor) => {
                    const points = Number(factor.points);
                    return (
                      <span key={factor.kind} className="flex items-start justify-between gap-3 text-xs">
                        <span>{factor.description}</span>
                        <span
                          className={cn(
                            "font-mono font-semibold",
                            points > 0 && "text-success",
                            points < 0 && "text-destructive",
                          )}
                        >
                          {factorPoints(factor)}
                        </span>
                      </span>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
