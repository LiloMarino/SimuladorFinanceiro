import { useState } from "react";
import { Search } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { Card } from "@/shared/components/ui/card";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { displayWeekdayDate } from "@/shared/lib/utils/display";
import type { NewsSection } from "@/types";
import { useNews } from "../hooks/queries/useNews";
import { filterNews, type JournalFilter } from "../lib/filter";
import { sectionOf } from "../lib/catalog";
import { JournalEntries } from "./journal-entries";
import { JournalSkeleton } from "./journal-skeleton";

const ALL = "ALL";

type JournalPaperProps = { simulationId: number };

/** O histórico da partida inteira em página de jornal: busca, seções, só minha carteira e as manchetes por dia. */
export function JournalPaper({ simulationId }: JournalPaperProps) {
  const news = useNews(simulationId);
  const { data: catalog, error: catalogError, refetch: refetchCatalog } = useNotificationCatalog();
  const { preferences } = useNotificationPreferences();
  const { data: portfolio } = usePortfolio();
  const { data: state } = useSimulationState();
  const [filter, setFilter] = useState<JournalFilter>({ query: "", section: null, onlyMine: false });

  const failed = news.error ?? catalogError;
  const held = new Set((portfolio?.variable_income ?? []).map((position) => position.ticker));

  return (
    <Card variant="paper" size="flush" className="min-h-[calc(100svh-9rem)]">
      {/* Cabeçalho do jornal */}
      <div className="grid gap-3 border-b-[3px] border-double border-foreground px-7 pt-4 pb-3">
        <div className="grid grid-cols-[1fr_auto_1fr] items-end">
          <span className="font-mono text-xs text-muted-foreground first-letter:uppercase">
            {state?.current_date ? displayWeekdayDate(state.current_date) : ""}
          </span>
          <h2 className="font-serif text-4xl font-bold tracking-tight">Diário do Pregão</h2>
          <span className="text-right font-mono text-xs text-muted-foreground">A partida inteira</span>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <InputGroup size="lg" className="w-85">
            <InputGroupAddon>
              <Search />
            </InputGroupAddon>
            <InputGroupInput
              value={filter.query}
              onChange={(e) => setFilter({ ...filter, query: e.target.value })}
              placeholder="Buscar manchete, empresa ou ticker"
              aria-label="Buscar no jornal"
            />
          </InputGroup>
          {catalog && (
            <Tabs
              value={filter.section ?? ALL}
              onValueChange={(value) =>
                setFilter({ ...filter, section: value === ALL ? null : (value as NewsSection) })
              }
            >
              <TabsList variant="line">
                <TabsTrigger value={ALL}>Tudo</TabsTrigger>
                {catalog.sections.map((section) => (
                  <TabsTrigger key={section.section} value={section.section}>
                    {section.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          )}
          <div className="ml-auto flex items-center gap-2">
            <Switch
              id="journal-only-mine"
              checked={filter.onlyMine}
              onCheckedChange={(onlyMine) => setFilter({ ...filter, onlyMine })}
            />
            <Label htmlFor="journal-only-mine">Só minha carteira</Label>
          </div>
        </div>
      </div>

      {/* Manchetes */}
      <div className="px-7 pb-6">
        {failed ? (
          <ErrorState
            title="Não deu para carregar as notícias"
            description="A partida segue normal. Tente de novo em instantes."
            error={failed}
            onRetry={() => void Promise.all([news.refetch(), refetchCatalog()])}
          />
        ) : !news.data || !catalog || !preferences ? (
          <JournalSkeleton />
        ) : (
          <JournalEntries
            items={filterNews(news.data, filter, {
              sectionOf: (type) => sectionOf(catalog, type),
              levelOf: (type) => preferences.news[type],
              held,
            })}
            total={news.data.length}
            filter={filter}
            onClear={() => setFilter({ query: "", section: null, onlyMine: false })}
            held={held}
          />
        )}
      </div>
    </Card>
  );
}
