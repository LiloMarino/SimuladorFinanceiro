import { z } from "zod";

export const investmentFormSchema = z.object({
  amount: z
    .string()
    .min(1, "Informe um valor")
    .refine((v) => Number(v) > 0, "O valor deve ser maior que zero"),
});

export type InvestmentFormSchema = z.infer<typeof investmentFormSchema>;
