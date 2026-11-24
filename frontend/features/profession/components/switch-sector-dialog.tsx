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
import { PROFESSIONS } from "@/shared/lib/professions";
import { displayMoney, displayNumber } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useSwitchSector } from "../hooks/mutations/useSwitchSector";

type AdministratorMechanic = Extract<ProfessionMechanic, { kind: "administrator" }>;

type SwitchSectorDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mechanic: AdministratorMechanic;
  target: AdministratorMechanic["sectors"][number];
};

/** "Trocar de setor": a renda do mês da troca e a renda que o setor novo paga com a experiência de hoje. */
export function SwitchSectorDialog({ open, onOpenChange, mechanic, target }: SwitchSectorDialogProps) {
  const switchSector = useSwitchSector();
  const name = PROFESSIONS[target.sector].name;

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Trocar para o setor {name}?</AlertDialogTitle>
          <AlertDialogDescription>
            A troca leva 1 mês, e nele a renda é a metade: {displayMoney(mechanic.switch_month_income)}. Depois você
            leva {displayMoney(target.income)} por mês no {name}, com nível de {displayNumber(target.level, 2)}× pela
            experiência de hoje. Leva só a renda do setor, sem a mecânica dele.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Agora não</AlertDialogCancel>
          <Button
            disabled={switchSector.isPending}
            onClick={() => switchSector.mutate({ sector: target.sector }, { onSuccess: () => onOpenChange(false) })}
          >
            Trocar
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
