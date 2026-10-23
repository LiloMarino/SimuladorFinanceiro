import { cva } from "class-variance-authority";
import { gradeTone } from "@/shared/lib/credit";
import { cn } from "@/shared/lib/utils";
import type { CreditGrade } from "@/types";

const gradeMarkVariants = cva(
  "inline-flex shrink-0 items-center justify-center rounded-xl font-mono font-bold tracking-tight ring-1 ring-inset",
  {
    variants: {
      tone: {
        success: "bg-success-soft text-success ring-success/25",
        warning: "bg-warning-soft text-warning ring-warning/25",
        destructive: "bg-destructive-soft text-destructive ring-destructive/25",
      },
      size: {
        md: "size-14 text-2xl",
        lg: "size-16 text-[27px]",
      },
    },
    defaultVariants: { size: "lg" },
  },
);

type CreditGradeMarkProps = {
  grade: CreditGrade;
  size?: "md" | "lg";
};

/** A letra da nota de risco num selo cuja cor acompanha a faixa da nota. */
export function CreditGradeMark({ grade, size }: CreditGradeMarkProps) {
  return (
    <span className={cn(gradeMarkVariants({ tone: gradeTone(grade), size }))} aria-label={`Nota ${grade}`}>
      {grade}
    </span>
  );
}
