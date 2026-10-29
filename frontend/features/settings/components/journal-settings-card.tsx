import { useState } from "react";
import { Lock, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Label } from "@/shared/components/ui/label";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import type { NewsLevel, NewsTypeInfo } from "@/types";

const LEVELS: { level: NewsLevel; label: string }[] = [
  { level: "WINDOW", label: "Janela" },
  { level: "JOURNAL", label: "Jornal" },
  { level: "HISTORY_ONLY", label: "Só no histórico" },
  { level: "OFF", label: "Desligado" },
];

/** O nível de cada tipo de manchete, agrupado por seção; o tipo fixo mostra o selo no lugar da escolha. */
export function JournalSettingsCard() {
  const { preferences, updatePreferences } = useNotificationPreferences();
  const { data: catalog } = useNotificationCatalog();
  const [failure, setFailure] = useState<string | null>(null);

  const save = (news: Record<string, NewsLevel>, failureText: string, newsHeldOnly = preferences?.news_held_only) => {
    if (!preferences) return;
    setFailure(null);
    updatePreferences(
      { ...preferences, news, news_held_only: newsHeldOnly ?? {} },
      { onError: () => setFailure(failureText) },
    );
  };

  const changeHeldOnly = (spec: NewsTypeInfo, onlyHeld: boolean) => {
    if (!preferences) return;
    save(preferences.news, `Não salvou: “${spec.label}” voltou ao filtro anterior.`, {
      ...preferences.news_held_only,
      [spec.type]: onlyHeld,
    });
  };

  const change = (spec: NewsTypeInfo, level: NewsLevel) => {
    if (!preferences) return;
    save({ ...preferences.news, [spec.type]: level }, `Não salvou: “${spec.label}” voltou ao nível anterior.`);
  };

  const restoreDefaults = () => {
    if (!catalog) return;
    save(
      Object.fromEntries(catalog.news.map((spec) => [spec.type, spec.default_level])),
      "Não salvou: o padrão não foi restaurado.",
      {},
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Jornal</CardTitle>
        <CardDescription>
          O que acontece no mercado e no país. Janela: a manchete abre no centro, sem pausar, e fecha sozinha. Jornal:
          vira cartão no canto. Só no histórico: fica na página do jornal.
        </CardDescription>
        <CardAction>
          <Button variant="outline" size="sm" onClick={restoreDefaults} disabled={!catalog || !preferences}>
            Restaurar padrão
          </Button>
        </CardAction>
      </CardHeader>
      {/* Lista de tipos, de borda a borda do cartão */}
      <div>
        {catalog && preferences ? (
          catalog.sections.map((section) => (
            <div key={section.section}>
              {/* Seção */}
              <div className="flex items-baseline gap-2 border-t bg-subtle px-5 pt-3 pb-1.5">
                <span className="text-[10.5px] font-bold tracking-widest uppercase">{section.label}</span>
                {section.note && <span className="text-xs text-muted-foreground">{section.note}</span>}
              </div>
              {/* Tipos da seção */}
              {catalog.news
                .filter((spec) => spec.section === section.section)
                .map((spec) => (
                  <div key={spec.type} className="flex items-center gap-4 border-t border-muted px-5 py-2.5">
                    <span className="grid min-w-0 flex-1">
                      <span className="font-medium">{spec.label}</span>
                      <span className="text-xs text-muted-foreground">{spec.description}</span>
                      {spec.portfolio_filter && (
                        <span className="mt-1.5 flex items-center gap-2">
                          <Switch
                            id={`held-only-${spec.type}`}
                            size="sm"
                            checked={preferences.news_held_only[spec.type] ?? false}
                            onCheckedChange={(checked) => changeHeldOnly(spec, checked)}
                          />
                          <Label htmlFor={`held-only-${spec.type}`}>Só ativos da minha carteira</Label>
                        </span>
                      )}
                    </span>
                    {spec.fixed ? (
                      <Badge variant="inverse" size="tag">
                        <Lock />
                        Janela com pausa
                      </Badge>
                    ) : (
                      <ToggleGroup
                        variant="segmented"
                        aria-label={spec.label}
                        value={[preferences.news[spec.type] ?? spec.default_level]}
                        onValueChange={(values) => {
                          const next = LEVELS.find((option) => option.level === values[0]);
                          if (next) change(spec, next.level);
                        }}
                      >
                        {LEVELS.map((option) => (
                          <ToggleGroupItem key={option.level} value={option.level}>
                            {option.label}
                          </ToggleGroupItem>
                        ))}
                      </ToggleGroup>
                    )}
                  </div>
                ))}
            </div>
          ))
        ) : (
          <Skeleton className="mx-5 mb-5 h-64 w-auto" />
        )}
        {failure && (
          <Alert variant="destructive" className="mx-5 mb-5 w-auto">
            <TriangleAlert />
            <AlertDescription>{failure}</AlertDescription>
          </Alert>
        )}
      </div>
    </Card>
  );
}
