import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { Button } from "@/shared/components/ui/button";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useEnrollStep } from "../hooks/mutations/useEnrollStep";
import { displayMultiple, displayStepDuration, STEP_TEXTS, type GraduateStep } from "../lib/graduate-steps";

type EnrollStepDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mechanic: Extract<ProfessionMechanic, { kind: "graduate" }>;
  step: GraduateStep;
};

/** "Matricular no degrau": a duração, o que o degrau custa no lugar do salário e o múltiplo que a conclusão leva. */
export function EnrollStepDialog({ open, onOpenChange, mechanic, step }: EnrollStepDialogProps) {
  const enroll = useEnrollStep();
  const text = STEP_TEXTS[step.step];
  const duration = displayStepDuration(step.months);

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Matricular {text.inside}?</AlertDialogTitle>
          <AlertDialogDescription>
            {step.stipend !== null
              ? `Por ${duration} a bolsa de ${displayMoney(step.stipend)} por mês paga no lugar do salário de ${displayMoney(mechanic.salary)}, isenta de imposto e sem risco de demissão.`
              : `Por ${duration} você trabalha junto e paga a mensalidade de ${displayMoney(step.tuition ?? 0)} por mês.`}{" "}
            Ao concluir, o múltiplo do fim da carreira sobe de {displayMultiple(mechanic.final_multiple)} para{" "}
            {displayMultiple(step.final_multiple)}.
            {step.unemployment_discount &&
              ` Com o desemprego em ${displayPercent(mechanic.unemployment, 1, { trim: true })}, acima do neutro, ${
                step.stipend !== null
                  ? `a bolsa fica ${displayPercent(mechanic.stipend_bonus_rate, 0)} maior`
                  : `a mensalidade fica ${displayPercent(mechanic.tuition_discount_rate, 0)} menor`
              } até o fim do degrau.`}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Agora não</AlertDialogCancel>
          <Button
            disabled={enroll.isPending}
            onClick={() => enroll.mutate({ step: step.step }, { onSuccess: () => onOpenChange(false) })}
          >
            Matricular
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
