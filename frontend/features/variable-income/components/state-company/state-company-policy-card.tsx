import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { POLICY_LABEL } from "@/shared/lib/state-company";
import type { StateCompanyDetail } from "@/types";
import { policyDescription } from "../../lib/state-company";

type StateCompanyPolicyCardProps = Pick<StateCompanyDetail, "policies" | "dividend_policy">;

/** As políticas de dividendos, com a que vale hoje marcada. */
export function StateCompanyPolicyCard({ policies, dividend_policy: current }: StateCompanyPolicyCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Política de dividendos</CardTitle>
        <CardDescription>Quem escolhe é o presidente, na aba Estatais do governo.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2">
          {policies.map((option) => {
            const policy = option.dividend_policy;
            const active = policy === current;
            return (
              <div
                key={policy}
                className={cn(
                  "grid gap-0.5 rounded-[10px] border px-3 py-2.5",
                  active ? "border-2 border-expansion-government bg-expansion-government-soft" : "bg-card",
                )}
              >
                <div className="flex items-center gap-2 font-semibold">
                  {POLICY_LABEL[policy]}
                  {active && (
                    <Badge variant="state-soft" size="tag">
                      agora
                    </Badge>
                  )}
                </div>
                <div className="text-[13px] text-muted-foreground">{policyDescription(option)}</div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
