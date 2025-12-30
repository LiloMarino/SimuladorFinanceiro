import { z } from "zod";

export const ApiResponseSchema = z.object({
  status: z.enum(["success", "error"]),
  message: z.string(),
  data: z.any(),
});
