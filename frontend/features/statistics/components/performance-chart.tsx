import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/shared/components/ui/tabs";

const TABS = [
  { key: "total", label: "Patrimônio Total" },
  { key: "variable", label: "Renda Variável" },
  { key: "fixed", label: "Renda Fixa" },
  { key: "cash", label: "Caixa" },
];

export function PerformanceChart() {
  return (
    <Card>
      <CardHeader className="space-y-4">
        <CardTitle>Desempenho da Partida</CardTitle>

        <Tabs defaultValue="total">
          <TabsList>
            {TABS.map((tab) => (
              <TabsTrigger key={tab.key} value={tab.key}>
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {TABS.map((tab) => (
            <TabsContent key={tab.key} value={tab.key}>
              <div className="h-72 w-full rounded-md border border-dashed flex items-center justify-center text-sm text-muted-foreground">
                Gráfico de {tab.label}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </CardHeader>

      {/* CardContent vazio por enquanto, Tabs já ocupam tudo */}
      <CardContent />
    </Card>
  );
}
