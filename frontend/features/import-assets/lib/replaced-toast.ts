import { toast } from "sonner";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { ReplacedGenerated } from "@/types";

const dayMonth = (iso: string) => displayDate(parseLocalDate(iso)).slice(0, 5);

/** O real que chegou e ocupou o lugar do gerado; sem dias trocados, nada a avisar. */
export function toastReplacedGenerated(key: string, replaced: ReplacedGenerated | null) {
  if (!replaced) return;
  const sameYear = replaced.start.slice(0, 4) === replaced.end.slice(0, 4);
  const start = sameYear ? dayMonth(replaced.start) : displayDate(parseLocalDate(replaced.start));
  const entered =
    replaced.days === 1 ? "1 pregão real entrou" : `${replaced.days} pregões reais entraram`;
  toast.success(`${key} atualizada`, {
    description: `${entered} no lugar do gerado, de ${start} a ${displayDate(parseLocalDate(replaced.end))}. Gere de novo para emendar o futuro.`,
  });
}
