import { z } from "zod";

export const ApiResponseSchema = z.object({
  data: z.any(),
});
