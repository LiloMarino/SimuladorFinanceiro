import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { CompositionTab } from "./composition-tab";
import { OperationsTab } from "./operations-tab";
import { OverviewTab } from "./overview-tab";
import { ReturnsTab } from "./returns-tab";
import { RiskTab } from "./risk-tab";
import type { ReportProps } from "./shared";

const TABS = [
  { value: "overview", label: "Geral", Content: OverviewTab },
  { value: "returns", label: "Rentabilidade", Content: ReturnsTab },
  { value: "risk", label: "Risco", Content: RiskTab },
  { value: "composition", label: "Composição", Content: CompositionTab },
  { value: "operations", label: "Operações", Content: OperationsTab },
] as const;

/**
 * Relatório de desempenho em abas, como o fim de partida de um RTS. Serve a partida em
 * andamento, o fechamento e a comparação: muda só a lista de simulações. Cada aba busca
 * os próprios dados quando é aberta.
 */
export function StatisticsReport({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  return (
    <Tabs defaultValue={TABS[0].value} className="space-y-4">
      <TabsList className="flex-wrap h-auto">
        {TABS.map((tab) => (
          <TabsTrigger key={tab.value} value={tab.value}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>

      {TABS.map(({ value, Content }) => (
        <TabsContent key={value} value={value}>
          <Content
            simulationIds={simulationIds}
            showSimulation={showSimulation}
            currentPlayerName={currentPlayerName}
          />
        </TabsContent>
      ))}
    </Tabs>
  );
}
