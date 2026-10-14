import { toast } from "sonner";
import type ApiError from "@/shared/lib/models/ApiError";

/** Erro da API em toast: a mensagem em português e a linha técnica embaixo. */
export function toastApiError(err: ApiError, options?: { id?: string | number }) {
  toast.error(err.message, { description: err.statusLine, ...options });
}
