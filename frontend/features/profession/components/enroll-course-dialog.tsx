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
import { displayMoney } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useEnrollCourse } from "../hooks/mutations/useEnrollCourse";

type EnrollCourseDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mechanic: Extract<ProfessionMechanic, { kind: "welfare" }>;
};

/** "Matricular no curso técnico": o que o curso custa na renda do bico e o que a conclusão muda. */
export function EnrollCourseDialog({ open, onOpenChange, mechanic }: EnrollCourseDialogProps) {
  const enroll = useEnrollCourse();

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Matricular no curso técnico?</AlertDialogTitle>
          <AlertDialogDescription>
            Por {mechanic.course_months} meses a renda do bico cai pela metade, de {displayMoney(mechanic.gig_income)}{" "}
            para {displayMoney(mechanic.gig_income_in_course)}; o benefício, o Pé-de-Meia e a tarifa social continuam.
            Ao concluir, você vira CLT com salário de {displayMoney(mechanic.clt_salary)}: perde a tarifa social e o
            benefício, e o saldo de {displayMoney(mechanic.balance)} do Pé-de-Meia cai no seu caixa.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Agora não</AlertDialogCancel>
          <Button
            disabled={enroll.isPending}
            onClick={() => enroll.mutate(undefined, { onSuccess: () => onOpenChange(false) })}
          >
            Matricular
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
