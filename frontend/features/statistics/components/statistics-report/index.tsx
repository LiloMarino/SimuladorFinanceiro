import type { ComponentType } from "react";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { CompositionTab } from "./composition-tab";
import { OperationsTab } from "./operations-tab";
import { OverviewTab } from "./overview-tab";
import { ReturnsTab } from "./returns-tab";
import { RiskTab } from "./risk-tab";
import type { ReportProps } from "./shared";
import { SummariesTab } from "../summaries/summaries-tab";

const TABS = [
  { value: "overview", label: "Geral", Content: OverviewTab },
  { value: "returns", label: "Rentabilidade", Content: ReturnsTab },
  { value: "risk", label: "Risco", Content: RiskTab },
  { value: "composition", label: "Composição", Content: CompositionTab },
  { value: "operations", label: "Operações", Content: OperationsTab },
] as const;

const SUMMARIES_TAB = { value: "summaries", label: "Resumos" } as const;

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
  summariesFor,
  tab,
  onTabChange,
}: ReportProps & {
  /** Com título, as abas ficam no cabeçalho de um card, na mesma linha dele */
  title?: string;
  /** O conteúdo da aba Geral, para quem tem um Geral próprio (o backtest) */
  overview?: ComponentType<ReportProps>;
  /** A partida cujos resumos do mês e do ano ganham a aba Resumos; sem ela, a aba não existe */
  summariesFor?: number;
  /** A aba aberta, quando quem usa o relatório a controla (por exemplo, pela URL) */
  tab?: string | undefined;
  onTabChange?: (tab: string) => void;
}) {
  const triggers = summariesFor === undefined ? TABS : [...TABS, SUMMARIES_TAB];
  const tabState =
    onTabChange === undefined
      ? { defaultValue: TABS[0].value }
      : {
          value: triggers.find((trigger) => trigger.value === tab)?.value ?? TABS[0].value,
          onValueChange: (value: unknown) => onTabChange(String(value)),
        };
  const tabs = (
    <TabsList>
      {triggers.map((trigger) => (
        <TabsTrigger key={trigger.value} value={trigger.value}>
          {trigger.label}
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

  const summaries = summariesFor !== undefined && (
    <TabsContent value={SUMMARIES_TAB.value}>
      <SummariesTab simulationId={summariesFor} />
    </TabsContent>
  );

  return (
    <Tabs {...tabState}>
      {title ? (
        <Card>
          <CardHeader>
            <CardTitle>{title}</CardTitle>
            <CardAction>{tabs}</CardAction>
          </CardHeader>
          <CardContent>
            {contents}
            {summaries}
          </CardContent>
        </Card>
      ) : (
        <>
          {tabs}
          {contents}
          {summaries}
        </>
      )}
    </Tabs>
  );
}
