import { useState } from "react";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Switch } from "@/shared/components/ui/switch";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import type { NotificationPreferences } from "@/types";

type Option = {
  [Section in keyof NotificationPreferences]: {
    section: Section;
    item: keyof NotificationPreferences[Section];
    label: string;
    description: string;
  };
}[keyof NotificationPreferences];

const OPTIONS: Option[] = [
  { section: "orders", item: "executed", label: "Ordem executada", description: "Compra ou venda concluída" },
  { section: "orders", item: "partial", label: "Ordem executada em parte", description: "Faltou contraparte no book" },
  {
    section: "players",
    item: "join_exit",
    label: "Entrada e saída de jogadores",
    description: "Alguém entrou ou saiu da sala",
  },
];

/** Os avisos do canto da tela; um que não salvou volta ao valor anterior e diz isso no lugar. */
export function NotificationsCard() {
  const { preferences, updatePreferences } = useNotificationPreferences();
  const [failure, setFailure] = useState<string | null>(null);

  const valueOf = (o: Option) => (preferences[o.section] as Record<string, boolean>)[o.item];

  const change = (o: Option, checked: boolean) => {
    setFailure(null);
    updatePreferences(
      { ...preferences, [o.section]: { ...preferences[o.section], [o.item]: checked } },
      { onError: () => setFailure(`Não salvou: “${o.label}” voltou a ficar ${checked ? "desligado" : "ligado"}.`) },
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Avisos</CardTitle>
        <CardDescription>Quais avisos aparecem no canto da tela durante a partida.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid">
          {OPTIONS.map((o) => (
            <label
              key={`${o.section}.${o.item}`}
              className="flex cursor-pointer items-center justify-between gap-3 border-t border-muted py-2.5"
            >
              <span className="grid">
                <span className="font-medium">{o.label}</span>
                <span className="text-xs text-muted-foreground">{o.description}</span>
              </span>
              <Switch checked={valueOf(o)} onCheckedChange={(checked) => change(o, checked)} />
            </label>
          ))}
          {failure && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertDescription>{failure}</AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
