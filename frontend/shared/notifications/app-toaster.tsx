import { Toaster } from "@/shared/components/ui/sonner";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";

// A coluna do menu lateral (14.5rem em MainLayout) mais a margem do canto
const SIDEBAR_OFFSET = "calc(14.5rem + 1.5rem)";

/**
 * Os toasts ficam embaixo, no lado oposto ao do jornal; com o jornal em cima ou na faixa,
 * embaixo à direita.
 */
export function AppToaster() {
  const { preferences } = useNotificationPreferences();

  if (preferences?.news_position === "BOTTOM_RIGHT") {
    return <Toaster position="bottom-left" offset={{ left: SIDEBAR_OFFSET, bottom: "1.5rem" }} />;
  }
  return <Toaster position="bottom-right" />;
}
