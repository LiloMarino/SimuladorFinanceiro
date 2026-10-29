import { useEffect, useEffectEvent, useRef } from "react";
import { toast } from "sonner";
import type { Pending } from "@/types";
import { bornSince, pendingTarget } from "../lib/pending";

/**
 * Cada pendência que nasce depois da primeira leitura sobe um toast, uma vez; as que já
 * existiam ao abrir a partida ficam só na lista.
 */
export function usePendingToasts(items: Pending[] | undefined, onAct: (item: Pending) => void) {
  const known = useRef<ReadonlySet<string> | null>(null);
  const act = useEffectEvent(onAct);

  useEffect(() => {
    if (!items) return;
    if (known.current) {
      for (const item of bornSince(known.current, items)) {
        const show = item.severity === "SEVERE" ? toast.error : toast.warning;
        show(`Nova pendência: ${item.title.toLocaleLowerCase("pt-BR")}`, {
          id: item.key,
          description: item.detail,
          action: { label: pendingTarget(item).label, onClick: () => act(item) },
        });
      }
    }
    known.current = new Set(items.map((item) => item.key));
  }, [items]);
}
