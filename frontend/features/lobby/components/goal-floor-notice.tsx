import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { MetricHint } from "@/shared/components/metric-hint";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import { MINIMUM_GOAL } from "@/shared/lib/life-metrics";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import { withdrawalRateFraction } from "../lib/life-rules";
import {
  heirFloorMessage,
  maximumWithdrawalPercent,
  minimumExpense,
  minimumGoal,
  type RoomHeir,
} from "../lib/minimum-goal";

type GoalFloorNoticeProps = {
  heir: RoomHeir;
  expense: string;
  rate: string;
};

/** O aviso da meta do viver de renda abaixo do capital do Herdeiro, com a despesa e a taxa (válidas) que a fazem passar. */
export function GoalFloorNotice({ heir, expense, rate }: GoalFloorNoticeProps) {
  const suggestedExpense = minimumExpense(heir.capital, withdrawalRateFraction(rate));
  const suggestedRate = maximumWithdrawalPercent(heir.capital, Number(normalizeNumberString(expense)));
  const who = heir.isBot ? `O bot ${heir.nickname}` : heir.nickname;

  return (
    <Alert variant="destructive">
      <div className="flex items-center gap-1">
        <AlertTitle>{heirFloorMessage(heir.capital)}</AlertTitle>
        <MetricHint metric={MINIMUM_GOAL} />
      </div>
      <AlertDescription>
        {who} começa com {displayMoneyWhole(minimumGoal(heir.capital))} e venceria no primeiro dia. Suba a despesa para{" "}
        {displayMoneyWhole(suggestedExpense)}
        {suggestedRate !== null && <> ou baixe a taxa de retirada para {displayRatePercent(suggestedRate / 100)}</>}.
      </AlertDescription>
    </Alert>
  );
}
