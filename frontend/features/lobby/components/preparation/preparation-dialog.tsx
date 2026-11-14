import { useState } from "react";
import { Briefcase, Flag, IdCard, SlidersHorizontal } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { Badge } from "@/shared/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/shared/components/ui/dialog";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { useAuth } from "@/shared/hooks/useAuth";
import { useBotStrategies } from "@/shared/hooks/queries/useBotStrategies";
import { useBotTickers } from "@/shared/hooks/queries/useBotTickers";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSavedStrategyParams } from "@/shared/hooks/queries/useSavedStrategyParams";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import type { SimulationSettings } from "@/types";
import { useMyFund } from "../../hooks/queries/useMyFund";
import { useMyParty } from "../../hooks/queries/useMyParty";
import { useMyPreparation } from "../../hooks/queries/useMyPreparation";
import { usePartyContribution } from "../../hooks/queries/usePartyContribution";
import { usePreparations } from "../../hooks/queries/usePreparations";
import { fundTabBadge } from "../../lib/fund-preparation";
import { adjustedStrategies } from "../../lib/preparation";
import { FundTab } from "./fund-tab";
import { PartyTab } from "./party-tab";
import { ProfessionTab } from "./profession-tab";
import { StrategiesTab } from "./strategies-tab";

type Tab = "profession" | "party" | "strategies" | "fund";

type PreparationDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  rules: SimulationSettings["simulation"];
  selectedSimulationId: SimulationSettings["selected_simulation_id"];
  /** As regras da sala dão uma profissão a cada jogador */
  professions: boolean;
  /** Quem jogou a partida salva selecionada: a profissão deles fica guardada */
  savedPlayers: SimulationSettings["selected_players"];
};

/** "Minha preparação": a profissão, o partido e os parâmetros das estratégias que o jogador refaz igual em toda partida. */
export function PreparationDialog({ open, onOpenChange, ...content }: PreparationDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        flush
        className="h-[min(52rem,calc(100vh-4rem))] grid-rows-[auto_minmax(0,1fr)] overflow-hidden sm:max-w-235"
      >
        <PreparationDialogContent {...content} onClose={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}

type PreparationDialogContentProps = Omit<PreparationDialogProps, "open" | "onOpenChange"> & { onClose: () => void };

/** Resolve o que as abas usam: cada aba monta com o dado pronto e o formulário nasce preenchido. */
function PreparationDialogContent({
  rules,
  selectedSimulationId,
  professions,
  savedPlayers,
  onClose,
}: PreparationDialogContentProps) {
  const [tab, setTab] = useState<Tab>(professions ? "profession" : "party");
  const preparations = usePreparations();
  const mine = useMyPreparation();
  const party = useMyParty();
  const fund = useMyFund();
  const contribution = usePartyContribution();
  const room = useRoomPlayers();
  const simulations = useSimulationList();
  const strategies = useBotStrategies(rules.start_date);
  const tickers = useBotTickers();
  const saved = useSavedStrategyParams();
  const { user } = useAuth();

  const failed = [preparations, mine, party, fund, contribution, room, strategies, saved, tickers].find(
    (query) => query.error,
  );
  const savedSimulation = simulations.data?.find((simulation) => simulation.id === selectedSimulationId);
  const adjusted =
    strategies.data && saved.data && tickers.data
      ? adjustedStrategies(strategies.data, saved.data, tickers.data)
      : new Set<string>();
  const savedSimulationName = selectedSimulationId ? (savedSimulation?.name ?? "partida salva") : null;
  // A profissão da partida salva fica com ela; quem entra como jogador novo escolhe antes de entrar
  const hasSavedProfession = !!user && savedPlayers.some((player) => player.nickname === user.nickname);
  const fundBadge =
    preparations.data && user ? fundTabBadge(rules.funds_enabled, preparations.data, user.nickname) : null;
  const myProfession = room.data?.find((player) => player.nickname === user?.nickname)?.profession;

  return (
    <Tabs value={tab} onValueChange={(value) => setTab(value as Tab)} className="contents">
      {/* Cabeçalho */}
      <div className="border-b px-6 pt-5 pr-14">
        <DialogTitle large>Minha preparação</DialogTitle>
        <DialogDescription>O que você refaz igual em toda partida. Vale no 1º dia da partida.</DialogDescription>
        <TabsList variant="line" className="mt-3.5 -mb-px">
          <TabsTrigger value="profession" disabled={!professions} className="flex-none">
            <IdCard /> Profissão
            {!professions && (
              <Badge variant="outline" size="sm">
                desligada nas regras
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="party" className="flex-none">
            <Flag /> Partido
          </TabsTrigger>
          <TabsTrigger value="strategies" className="flex-none">
            <SlidersHorizontal /> Estratégias
            {adjusted.size > 0 && (
              <Badge variant="info" size="sm">
                {adjusted.size} {adjusted.size === 1 ? "ajustada" : "ajustadas"}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="fund" className="flex-none">
            <Briefcase /> Gestora
            {fundBadge && (
              <Badge variant={fundBadge.variant} size="sm" numeric={fundBadge.variant === "fund"}>
                {fundBadge.label}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>
      </div>

      {failed?.error ? (
        <div className="p-6">
          <ErrorState
            title="Não deu para carregar a sua preparação"
            description="Sem o perfil e a sala, não dá para montar a preparação."
            error={failed.error}
            onRetry={() => void failed.refetch()}
          />
        </div>
      ) : (
        <>
          <TabsContent value="profession" className="grid min-h-0">
            {room.data && user ? (
              <ProfessionTab
                current={myProfession}
                lockedBy={hasSavedProfession ? savedSimulationName : null}
                joiningNew={savedPlayers.length > 0 && !hasSavedProfession ? savedSimulationName : null}
                room={rules}
                onClose={onClose}
              />
            ) : (
              <ProfessionSkeleton />
            )}
          </TabsContent>
          <TabsContent value="party" className="grid min-h-0">
            {preparations.data && mine.data && party.isSuccess && contribution.data && room.data && user ? (
              <PartyTab
                preparations={preparations.data}
                mine={mine.data}
                saved={party.data}
                contribution={contribution.data.amount}
                humans={room.data.filter((player) => !player.bot)}
                nickname={user.nickname}
                rules={rules}
                savedSimulation={savedSimulationName}
                onStrategies={() => setTab("strategies")}
                onClose={onClose}
              />
            ) : (
              <PreparationSkeleton />
            )}
          </TabsContent>
          <TabsContent value="strategies" className="grid min-h-0">
            {strategies.data && saved.data && tickers.data ? (
              <StrategiesTab
                strategies={strategies.data}
                saved={saved.data}
                tickers={tickers.data}
                startingCash={rules.starting_cash}
                onClose={onClose}
              />
            ) : (
              <PreparationSkeleton />
            )}
          </TabsContent>
          <TabsContent value="fund" className="grid min-h-0">
            {preparations.data && fund.isSuccess && tickers.data && room.data && user ? (
              <FundTab
                preparations={preparations.data}
                saved={fund.data}
                humans={room.data.filter((player) => !player.bot)}
                assets={tickers.data}
                nickname={user.nickname}
                rules={rules}
                savedSimulation={savedSimulationName}
                onClose={onClose}
              />
            ) : (
              <PreparationSkeleton />
            )}
          </TabsContent>
        </>
      )}
    </Tabs>
  );
}

function ProfessionSkeleton() {
  return (
    <div className="grid content-start gap-4 p-6" aria-busy="true" aria-label="Carregando a sua preparação">
      <Skeleton className="h-5 w-1/3" />
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 6 }, (_, index) => (
          <Skeleton key={index} className="h-56 w-full" />
        ))}
      </div>
    </div>
  );
}

function PreparationSkeleton() {
  return (
    <div className="grid gap-4 p-6" aria-busy="true" aria-label="Carregando a sua preparação">
      <Skeleton className="h-9 w-full" />
      <div className="grid grid-cols-[1.15fr_1fr] gap-6">
        <div className="grid content-start gap-3">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <div className="grid content-start gap-3">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    </div>
  );
}
