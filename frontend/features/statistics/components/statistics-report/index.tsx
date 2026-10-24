import type { ComponentType } from "react";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
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
export function StatisticsReport({
  simulationIds,
  currentPlayerName,
  onlyPlayer,
  title,
  overview: Overview = OverviewTab,
}: ReportProps & {
  /** Com título, as abas ficam no cabeçalho de um card, na mesma linha dele */
  title?: string;
  /** O conteúdo da aba Geral, para quem tem um Geral próprio (o backtest) */
  overview?: ComponentType<ReportProps>;
}) {
  const tabs = (
    <TabsList>
      {TABS.map((tab) => (
        <TabsTrigger key={tab.value} value={tab.value}>
          {tab.label}
        </TabsTrigger>
      ))}
    </TabsList>
  );
  const contents = TABS.map(({ value, Content }) => {
    const Tab = value === "overview" ? Overview : Content;
    return (
      <TabsContent key={value} value={value}>
        <Tab simulationIds={simulationIds} currentPlayerName={currentPlayerName} onlyPlayer={onlyPlayer} />
      </TabsContent>
    );
  });

  return (
    <Tabs defaultValue={TABS[0].value}>
      {title ? (
        <Card>
          <CardHeader>
            <CardTitle>{title}</CardTitle>
            <CardAction>{tabs}</CardAction>
          </CardHeader>
          <CardContent>{contents}</CardContent>
        </Card>
      ) : (
        <>
          {tabs}
          {contents}
        </>
      )}
    </Tabs>
  );
}
