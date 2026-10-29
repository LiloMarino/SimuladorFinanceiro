import { useState } from "react";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { cn } from "@/shared/lib/utils";
import type { NewsPosition } from "@/types";

const POSITIONS: { position: NewsPosition; label: string; mark: string }[] = [
  { position: "BOTTOM_LEFT", label: "Embaixo à esquerda", mark: "bottom-1.5 left-1.5 h-4 w-8" },
  { position: "BOTTOM_RIGHT", label: "Embaixo à direita", mark: "right-1.5 bottom-1.5 h-4 w-8" },
  { position: "TOP_LEFT", label: "Em cima à esquerda", mark: "top-3.5 left-1.5 h-4 w-8" },
  { position: "STRIP", label: "Faixa sob a topbar", mark: "inset-x-0 top-2.5 h-2" },
];

/** Onde o jornal aparece na tela; os avisos ficam embaixo, no lado oposto. */
export function NewsPositionCard() {
  const { preferences, updatePreferences } = useNotificationPreferences();
  const [failure, setFailure] = useState<string | null>(null);

  const change = (position: NewsPosition) => {
    if (!preferences) return;
    setFailure(null);
    updatePreferences(
      { ...preferences, news_position: position },
      { onError: () => setFailure("Não salvou: o jornal voltou à posição anterior.") },
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Posição do jornal</CardTitle>
        <CardDescription>
          Onde o cartão de manchete aparece. Os avisos ficam embaixo, no lado oposto; com a faixa, embaixo à direita.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3">
          <RadioGroup
            value={preferences?.news_position ?? ""}
            onValueChange={(value) => change(value as NewsPosition)}
            className="grid-cols-2"
          >
            {POSITIONS.map((option) => {
              const selected = preferences?.news_position === option.position;
              return (
                <label
                  key={option.position}
                  className={cn(
                    "grid cursor-pointer gap-2 rounded-[10px] border p-2.5 text-[13px]",
                    selected && "border-primary bg-info-soft/60 ring-1 ring-primary",
                  )}
                >
                  {/* Esboço da tela */}
                  <span className="relative h-16 overflow-hidden rounded-md border bg-subtle">
                    <span className={cn("absolute rounded-sm bg-foreground/40", option.mark)} />
                  </span>
                  <span className="flex items-center gap-2">
                    <RadioGroupItem value={option.position} />
                    <span className="font-medium">{option.label}</span>
                  </span>
                </label>
              );
            })}
          </RadioGroup>
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
