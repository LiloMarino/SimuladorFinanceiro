import { useState } from "react";
import { Landmark, Newspaper, RefreshCw, TriangleAlert } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
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
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/shared/components/ui/field";
import { Progress } from "@/shared/components/ui/progress";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { STATE_LEVER_LABEL } from "@/shared/lib/state-lever";
import { displayMoneyLarge, displayPercent } from "@/shared/lib/utils/display";
import type { DividendPolicy, StateControl, StateLever, StateOrderPreview } from "@/types";
import { useSetStateOrder } from "../../hooks/mutations/useSetStateOrder";
import { useStateOrderPreview } from "../../hooks/queries/useStateOrderPreview";
import { BACKLOG, CONTROL_CAP, DIVIDEND_POLICY, PRICE_CONTROL } from "../../lib/government-metrics";
import { nextMonthLabel } from "../../lib/campaign";
import {
  POLICY_LABEL,
  POLICY_NOTE,
  capLabel,
  controlPercent,
  pointsLabel,
  stepEffect,
  stepLabel,
} from "../../lib/state-companies";

const CONTROL_TITLE: Record<StateLever, string> = {
  FUEL: "Controle do preço da gasolina",
  ENERGY: "Controle da conta de luz",
  BANK: "Controle do juro do crédito",
};

type CommandStateCompanyDialogProps = {
  /** A estatal que recebe a ordem */
  ticker: string;
  /** O dia da partida agora, para dizer desde quando a ordem vale */
  today: string;
  onClose: () => void;
};

/** A ordem do presidente numa estatal: controle de preço em degraus e política de dividendos, pelo que cada opção faria. */
export function CommandStateCompanyDialog({ ticker, today, onClose }: CommandStateCompanyDialogProps) {
  const preview = useStateOrderPreview(ticker);

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-230">
        {preview.data ? (
          <CommandForm preview={preview.data} today={today} onClose={onClose} />
        ) : (
          <>
            <DialogHeader variant="divided">
              <DialogTitle>Comandar uma estatal</DialogTitle>
              <DialogDescription>
                Ordem do presidente: controle de preço em degraus e política de dividendos.
              </DialogDescription>
            </DialogHeader>
            <DialogBody>
              {preview.error ? (
                <Alert variant="destructive">
                  <TriangleAlert />
                  <AlertTitle>Não deu para carregar a estatal</AlertTitle>
                  <AlertDescription>{preview.error.message}</AlertDescription>
                  <AlertAction>
                    <Button size="sm" variant="outline" onClick={() => void preview.refetch()}>
                      <RefreshCw />
                      Tentar de novo
                    </Button>
                  </AlertAction>
                </Alert>
              ) : (
                <div className="grid gap-3" aria-busy="true" aria-label="Carregando a estatal">
                  <Skeleton className="h-20 w-full" />
                  <Skeleton className="h-32 w-full" />
                </div>
              )}
            </DialogBody>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

type CommandFormProps = {
  preview: StateOrderPreview;
  today: string;
  onClose: () => void;
};

function CommandForm({ preview, today, onClose }: CommandFormProps) {
  const set = useSetStateOrder(preview.ticker);
  const [control, setControl] = useState<StateControl>(preview.order.control);
  const [policy, setPolicy] = useState<DividendPolicy>(preview.order.dividend_policy);

  const selected = preview.steps.find((step) => step.control === control);
  const cap = Number(preview.cap_points);
  const used = Number(preview.other_points) + Number(selected?.held_points ?? 0);
  const atCap = used >= cap;
  const highest = [...preview.steps].reverse().find((step) => step.control !== "NONE" && step.blocked_reason === null);
  const unchanged = control === preview.order.control && policy === preview.order.dividend_policy;
  const backlog = Number(preview.backlog_points);

  return (
    <>
      <DialogHeader variant="divided">
        <DialogTitle>Comandar a {preview.name}</DialogTitle>
        <DialogDescription>
          {preview.ticker}
          {preview.lever && ` · ${STATE_LEVER_LABEL[preview.lever].toLowerCase()}`}. É ordem sua: vale a partir de{" "}
          {nextMonthLabel(today)}.
        </DialogDescription>
      </DialogHeader>

      <DialogBody>
        <div className="grid gap-4">
          {/* Controle de preço */}
          {preview.lever ? (
            <FieldSet>
              <FieldLegend variant="label">
                <span className="inline-flex items-center gap-1.5">
                  {CONTROL_TITLE[preview.lever]}
                  <MetricHint metric={PRICE_CONTROL} />
                </span>
              </FieldLegend>
              <RadioGroup
                value={control}
                onValueChange={(value) => setControl(value as StateControl)}
                className="sm:grid-cols-5"
              >
                {preview.steps.map((step) => {
                  const effect = stepEffect(step, preview.lever);
                  return (
                    <FieldLabel key={step.control} htmlFor={`state-control-${step.control}`}>
                      <Field orientation="horizontal" data-disabled={step.blocked_reason !== null}>
                        <RadioGroupItem
                          value={step.control}
                          id={`state-control-${step.control}`}
                          disabled={step.blocked_reason !== null}
                        />
                        <FieldContent>
                          <FieldTitle className="w-full justify-between">
                            {stepLabel(step.control)}
                            <span className="font-mono text-xs">{effect?.main ?? "—"}</span>
                          </FieldTitle>
                          <FieldDescription>
                            {step.blocked_reason ?? effect?.dividend ?? "sem corte no dividendo"}
                          </FieldDescription>
                        </FieldContent>
                      </Field>
                    </FieldLabel>
                  );
                })}
              </RadioGroup>
              <p className="text-xs text-muted-foreground">
                Ponto do IPCA: com o IPCA em 6,0%, tirar 0,5 ponto mostra 5,5%. Dividendo: −30% quer dizer que o
                dividendo da empresa cai 30% com aquele degrau.
              </p>
            </FieldSet>
          ) : (
            <p className="text-[13px] text-muted-foreground">
              Esta estatal não tem alavanca de preço: só a política de dividendos vale.
            </p>
          )}

          {/* Teto do controle */}
          {preview.lever && (
            <div className="grid gap-1.5">
              <span className="flex items-center gap-1.5 text-[13px] font-semibold">
                Teto do controle, somando todas as estatais
                <MetricHint metric={CONTROL_CAP} />
              </span>
              <Progress
                value={cap > 0 ? Math.min(100, (used / cap) * 100) : 0}
                size="sm"
                indicatorTone={atCap ? "warning" : "default"}
                aria-label="Teto do controle de preço em uso"
              />
              <span className="text-xs text-muted-foreground">{capLabel(used, cap)} em uso</span>
              {highest && (
                <span className="text-xs text-muted-foreground">
                  {preview.name} pode ir até {controlPercent(highest.control)}% ({pointsLabel(highest.held_points)})
                </span>
              )}
            </div>
          )}

          {backlog > 0 && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertDescription>
                <b className="font-semibold">
                  {BACKLOG.label}: {BACKLOG.format(backlog)}.
                </b>{" "}
                O desconto fica guardado. Quando você soltar o controle, esses {pointsLabel(backlog)} voltam ao IPCA no
                mês seguinte.
              </AlertDescription>
            </Alert>
          )}

          {/* Política de dividendos */}
          <FieldSet>
            <FieldLegend variant="label">
              <span className="inline-flex items-center gap-1.5">
                Dividendos
                <MetricHint metric={DIVIDEND_POLICY} />
              </span>
            </FieldLegend>
            <RadioGroup
              value={policy}
              onValueChange={(value) => setPolicy(value as DividendPolicy)}
              className="sm:grid-cols-3"
            >
              {preview.policies.map((option) => (
                <FieldLabel key={option.dividend_policy} htmlFor={`state-policy-${option.dividend_policy}`}>
                  <Field orientation="horizontal">
                    <RadioGroupItem value={option.dividend_policy} id={`state-policy-${option.dividend_policy}`} />
                    <FieldContent>
                      <FieldTitle>
                        {POLICY_LABEL[option.dividend_policy]} · {displayPercent(option.payout, 0)}
                      </FieldTitle>
                      <FieldDescription>
                        <b className="block font-medium text-foreground">
                          {option.monthly_treasury_dividend === null
                            ? "Sem lucro modelado nesta estatal"
                            : `Tesouro recebe ${displayMoneyLarge(Number(option.monthly_treasury_dividend) * 12)} por ano`}
                        </b>
                        {POLICY_NOTE[option.dividend_policy]}
                        {option.dividend_policy === "REINVEST" &&
                          `. Pagar ${displayPercent(option.payout, 0)} do lucro é o mínimo da lei das S.A.`}
                      </FieldDescription>
                    </FieldContent>
                  </Field>
                </FieldLabel>
              ))}
            </RadioGroup>
            <p className="text-xs text-muted-foreground">
              {preview.order.control === "NONE"
                ? "Valores sem controle de preço, que é a ordem de hoje."
                : `Valores já com o controle de ${controlPercent(preview.order.control)}%, que é a ordem de hoje.`}
            </p>
          </FieldSet>

          {!preview.can_command && (
            <Alert variant="muted">
              <Landmark />
              <AlertTitle>Esta estatal não recebe ordem agora</AlertTitle>
              <AlertDescription>
                Com a privatização em curso, o controle e os dividendos ficam travados.
              </AlertDescription>
            </Alert>
          )}
          {set.isError && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>Não deu para dar a ordem</AlertTitle>
              <AlertDescription>{set.error.message}</AlertDescription>
            </Alert>
          )}
        </div>
      </DialogBody>

      <DialogFooter variant="divided" className="sm:justify-end">
        <span className="mr-auto flex items-center gap-1.5 text-xs text-muted-foreground">
          <Newspaper className="size-3.5" />
          Sai no jornal amanhã
        </span>
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button
          disabled={set.isPending || unchanged || !preview.can_command}
          onClick={() => set.mutate({ control, dividend_policy: policy }, { onSuccess: onClose })}
        >
          Dar a ordem
        </Button>
      </DialogFooter>
    </>
  );
}
