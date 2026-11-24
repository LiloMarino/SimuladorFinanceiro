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
import { useEnrollExam } from "../hooks/mutations/useEnrollExam";

type EnrollExamDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mechanic: Extract<ProfessionMechanic, { kind: "administrator" }>;
};

/** "Inscrever no concurso": o que o estudo custa na renda, a chance de aprovação e o que a aprovação muda. */
export function EnrollExamDialog({ open, onOpenChange, mechanic }: EnrollExamDialogProps) {
  const enroll = useEnrollExam();

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Inscrever no concurso para Servidor?</AlertDialogTitle>
          <AlertDialogDescription>
            Por {mechanic.exam_study_months} meses a renda cai {displayPercent(mechanic.exam_income_cut, 0)}, para{" "}
            {displayMoney(mechanic.exam_income)}. A chance de aprovação é de{" "}
            {displayPercent(mechanic.exam_pass_chance, 0)}. Aprovado, você vira Servidor com estabilidade, e a perde se
            sair; reprovado, volta à renda do setor e pode tentar o próximo edital.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Agora não</AlertDialogCancel>
          <Button
            disabled={enroll.isPending}
            onClick={() => enroll.mutate(undefined, { onSuccess: () => onOpenChange(false) })}
          >
            Inscrever
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
