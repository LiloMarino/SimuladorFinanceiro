import { z } from "zod";
import { normalizeNumberString } from "@/shared/lib/utils";

export const investmentFormSchema = z.object({
  amount: z
    .string()
    .min(1, "Informe um valor")
    .refine((val) => Number(normalizeNumberString(val)) > 0, "O valor deve ser maior que zero"),
});

export type InvestmentFormSchema = z.infer<typeof investmentFormSchema>;
