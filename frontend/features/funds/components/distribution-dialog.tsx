import { CalendarClock, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Slider } from "@/shared/components/ui/slider";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayIsoDate, displayMoney } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useSetFundDistribution } from "../hooks/mutations/useSetFundDistribution";
import { DISTRIBUTION_STEP, distributedOf, rateToBody, rateToPoints } from "../lib/fund-distribution";
import { DISTRIBUTION_RATE, REALIZED_PROFIT } from "@/shared/lib/fund-metrics";

type DistributionDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fund: FundDetails;
};

type DistributionFormProps = { fund: FundDetails; onOpenChange: (open: boolean) => void };

/** O lucro realizado do mês até hoje, por origem, e o que a parte escolhida distribuiria dele. */
function MonthBreakdown({ plan, points }: { plan: FundDetails["distribution"]; points: number }) {
  const profit = Number(plan.realized_profit);

  return (
    <div className="grid gap-2">
      <span className="text-sm font-medium">
        <MetricLabel metric={REALIZED_PROFIT} /> deste mês, até hoje
      </span>
      <div>
        <KeyValueRow label="Dividendos recebidos" value={displayMoney(plan.dividends)} />
        <KeyValueRow label="Juros da renda fixa" value={displayMoney(plan.interest)} />
        <KeyValueRow label="Ganho nas vendas" value={displayMoney(plan.sales_gain)} />
        <KeyValueRow label="Taxas pagas ao gestor" value={displayMoney(plan.fees)} />
        <KeyValueRow label="Lucro realizado" value={displayMoney(plan.realized_profit)} total />
      </div>
      <p className="rounded-lg bg-subtle px-3 py-2 text-xs text-muted-foreground">
        {profit > 0 ? (
          <>
            Com {points}%, esse lucro distribuiria{" "}
            <b className="font-mono font-semibold text-foreground">{displayMoney(distributedOf(profit, points))}</b> e
            deixaria {displayMoney(profit - distributedOf(profit, points))} no caixa.
          </>
        ) : (
          "Sem lucro realizado, o mês não distribui nada, e o prejuízo não passa para o mês seguinte."
        )}
      </p>
    </div>
  );
}

/** O formulário nasce a cada abertura: parte da parte em vigor, ou da pendente quando já há mudança marcada. */
function DistributionForm({ fund, onOpenChange }: DistributionFormProps) {
  const plan = fund.distribution;
  const start = rateToPoints(fund.pending_distribution_rate ?? fund.distribution_rate);
  const [points, setPoints] = useState(start);
  const setDistribution = useSetFundDistribution(fund.id);

  const submit = () =>
    setDistribution.mutate({ distribution_rate: rateToBody(points) }, { onSuccess: () => onOpenChange(false) });

  return (
    <>
      <DialogBody>
        <div className="grid gap-2">
          <div className="flex items-baseline justify-between gap-3">
            <span className="text-sm font-medium">
              <MetricLabel metric={DISTRIBUTION_RATE} />
            </span>
            <span className="font-mono text-[15px] font-semibold">{points}% do lucro realizado</span>
          </div>
          <Slider
            aria-label={DISTRIBUTION_RATE.label}
            min={0}
            max={100}
            step={DISTRIBUTION_STEP}
            value={points}
            onValueChange={setPoints}
          />
          <div className="flex justify-between font-mono text-xs text-muted-foreground">
            <span>0%</span>
            <span>100%</span>
          </div>
        </div>
        <MonthBreakdown plan={plan} points={points} />
        <div>
          <KeyValueRow label="Apuração (data-com)" value={displayIsoDate(plan.data_com_on)} />
          <KeyValueRow label="Pagamento aos cotistas" value={displayIsoDate(plan.pay_on)} />
        </div>
        {!plan.cash_enough && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertTitle>O caixa não cobre o rendimento deste mês</AlertTitle>
            <AlertDescription>
              A gestora tem {displayMoney(plan.cash)} e o mês renderia {displayMoney(plan.projected)}. Se o caixa não
              chegar na data do pagamento, cada cota recebe só o que o caixa dividido pelas cotas der, e a diferença não
              é devida depois.
            </AlertDescription>
          </Alert>
        )}
        <Alert variant="info">
          <CalendarClock />
          <AlertTitle>A parte nova vale no mês seguinte</AlertTitle>
          <AlertDescription>
            A mudança entra no primeiro dia útil do mês que vem, junto das taxas. O rendimento deste mês ainda sai pela
            parte de hoje.
          </AlertDescription>
        </Alert>
      </DialogBody>
      <DialogFooter variant="divided">
        <Button variant="outline" onClick={() => onOpenChange(false)}>
          Cancelar
        </Button>
        <Button variant="fund" disabled={points === start || setDistribution.isPending} onClick={submit}>
          {setDistribution.isPending && <Spinner />}
          Salvar a parte distribuída
        </Button>
      </DialogFooter>
    </>
  );
}

/** Mudar a parte do lucro realizado que vira rendimento; a mudança vale a partir do mês seguinte. */
export function DistributionDialog({ open, onOpenChange, fund }: DistributionDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Rendimentos de {fund.name}</DialogTitle>
          <DialogDescription>
            Quanto do lucro que a carteira realiza no mês vai para os cotistas, como num fundo imobiliário.
          </DialogDescription>
        </DialogHeader>
        <DistributionForm fund={fund} onOpenChange={onOpenChange} />
      </DialogContent>
    </Dialog>
  );
}
