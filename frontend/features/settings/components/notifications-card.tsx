import { useState } from "react";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Switch } from "@/shared/components/ui/switch";
import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import type { ToastType } from "@/types";

/** Os avisos do canto da tela, um interruptor por tipo; um que não salvou volta ao valor anterior e diz isso no lugar. */
export function NotificationsCard() {
  const { preferences, isToastOn, updatePreferences } = useNotificationPreferences();
  const { data: catalog } = useNotificationCatalog();
  const [failure, setFailure] = useState<string | null>(null);

  const change = (type: ToastType, label: string, checked: boolean) => {
    if (!preferences) return;
    setFailure(null);
    updatePreferences(
      { ...preferences, toasts: { ...preferences.toasts, [type]: checked } },
      { onError: () => setFailure(`Não salvou: “${label}” voltou a ficar ${checked ? "desligado" : "ligado"}.`) },
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Avisos</CardTitle>
        <CardDescription>Quais avisos pessoais aparecem no canto da tela durante a partida.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid">
          {catalog && preferences ? (
            catalog.toasts.map((toast) => (
              <label
                key={toast.type}
                className="flex cursor-pointer items-center justify-between gap-3 border-t border-muted py-2.5"
              >
                <span className="grid">
                  <span className="font-medium">{toast.label}</span>
                  <span className="text-xs text-muted-foreground">{toast.description}</span>
                </span>
                <Switch
                  checked={isToastOn(toast.type)}
                  onCheckedChange={(checked) => change(toast.type, toast.label, checked)}
                />
              </label>
            ))
          ) : (
            <Skeleton className="h-40 w-full" />
          )}
          {failure && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertDescription>{failure}</AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
