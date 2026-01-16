import { z } from "zod";

// Schema para respostas de erro da API
export const ApiErrorSchema = z.object({
  message: z.string(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;
