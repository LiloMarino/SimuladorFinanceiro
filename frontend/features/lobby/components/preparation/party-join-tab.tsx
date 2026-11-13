import { useState } from "react";
import { DoorOpen, Flag, Info, Users } from "lucide-react";
import { ContributionField } from "@/shared/components/contribution-field";
import { PartyMark } from "@/shared/components/party-mark";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { ValueChips } from "@/shared/components/value-chip";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { contributionAmount, contributionText } from "@/shared/lib/contribution";
import { cn } from "@/shared/lib/utils";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { PlayerPreparation, RoomPlayer } from "@/types";
import { useSavePartyContribution } from "../../hooks/mutations/useSavePartyContribution";
import { useSetPreparation } from "../../hooks/mutations/useSetPreparation";
import { useAutosave } from "../../hooks/useAutosave";
import { cashShare } from "../../lib/preparation";
import { PreparationFooter } from "./preparation-footer";
import { PreparationSection } from "./preparation-section";
import type { PartyModeProps } from "./party-tab";

const MEMBERS_SHOWN = 5;

/** Entrar num partido: os partidos que os jogadores da sala fundaram, a contribuição e quem decide a chapa. */
export function PartyJoinTab({
  preparations,
  mine,
  me,
  saved,
  contribution,
  humans,
  nickname,
  rules,
  savedSimulation,
  lead,
  locked,
  onMode,
  onClose,
}: PartyModeProps) {
  const joined = me?.kind === "JOIN" ? me.founder : null;
  const [founder, setFounder] = useState(joined);
  const [amount, setAmount] = useState(contributionText(contribution));
  const saveContribution = useSavePartyContribution();
  const prepare = useSetPreparation();

  // A contribuição vai para o perfil e só depois a escolha da sala, que parte do perfil
  const autosave = useAutosave({
    dirty:
      !locked &&
      founder !== null &&
      (founder !== joined || Number(contributionAmount(amount)) !== Number(contribution)),
    incomplete: null,
    signature: JSON.stringify({ founder, amount }),
    save: async () => {
      if (!founder) return;
      await saveContribution.mutateAsync(contributionAmount(amount));
      await prepare.mutateAsync({ kind: "JOIN", founder });
    },
  });

  const parties = preparations.players.filter((p) => p.kind === "FOUND" && p.party && p.nickname !== nickname);
  const chosen = parties.find((p) => p.nickname === founder);
  const membersOf = (owner: string) =>
    preparations.players.filter((p) => p.kind === "JOIN" && p.founder === owner).map((p) => p.nickname);

  return (
    <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 content-start gap-4.5 overflow-y-auto px-6 py-5">
        {lead}

        {/* Partido que saiu da sala */}
        {mine.left_party && (
          <Alert variant="warning">
            <DoorOpen />
            <AlertTitle>O {mine.left_party} saiu da preparação</AlertTitle>
            <AlertDescription>
              O fundador deixou a sala e o partido saiu junto. Você voltou para Sem partido; escolha outro abaixo ou
              funde o seu.
            </AlertDescription>
          </Alert>
        )}

        {parties.length === 0 ? (
          <Empty variant="dashed">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <Users />
              </EmptyMedia>
              <EmptyTitle>Ninguém preparou partido nesta sala</EmptyTitle>
              <EmptyDescription>
                Quando um jogador fundar o partido dele, ele aparece aqui para você entrar. Os partidos do computador
                não aceitam filiados.
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent>
              <Button type="button" variant="outline" onClick={() => onMode("FOUND")}>
                <Flag /> Fundar o meu partido
              </Button>
            </EmptyContent>
          </Empty>
        ) : (
          <fieldset disabled={locked} className="grid min-w-0 gap-4.5 disabled:opacity-55">
            {/* Partidos da sala */}
            <div className="grid gap-2">
              <div role="radiogroup" aria-label="Partido em que você entra" className="grid grid-cols-2 gap-3">
                {parties.map((party) => (
                  <PartyCard
                    key={party.nickname}
                    party={party}
                    members={membersOf(party.nickname)}
                    humans={humans}
                    state={party.nickname === joined ? "here" : party.nickname === founder ? "entering" : null}
                    onPick={() => setFounder(party.nickname)}
                  />
                ))}
              </div>
              <span className="text-xs text-muted-foreground">Os partidos do computador não aceitam filiados.</span>
            </div>

            {chosen?.party && (
              <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)] items-start gap-6">
                <PreparationSection title="Contribuição mensal" hint="vale fundando ou entrando">
                  <ContributionField
                    id="prep-join-contribution"
                    value={amount}
                    onChange={setAmount}
                    note={`${cashShare(contributionAmount(amount), rules.starting_cash)} do saldo inicial desta sala (${displayMoneyWhole(rules.starting_cash)}). Vai para o caixa do ${chosen.party.abbr} no 1º dia útil de cada mês da campanha. Mês sem caixa vira pendência.`}
                  />
                </PreparationSection>

                {/* Quem decide no partido */}
                <div className="grid gap-1.5 rounded-[10px] border px-3.5 py-3 text-[13px]">
                  <b className="font-semibold">No {chosen.party.abbr}, quem decide</b>
                  <span className="text-muted-foreground">
                    {chosen.nickname}, o fundador, escolhe o candidato entre os filiados e convida o vice. Você pode ser
                    escolhido para qualquer um dos dois.
                  </span>
                  <span className="text-muted-foreground">
                    Sair do partido é trocar a escolha acima, a qualquer momento antes do início.
                  </span>
                </div>
              </div>
            )}
          </fieldset>
        )}

        {/* Partido salvo no perfil */}
        {saved && (
          <Alert variant="muted">
            <Info />
            <AlertTitle>
              <span className="inline-flex items-center gap-2">
                Seu partido continua salvo <PartyMark abbr={saved.abbr} color={saved.color} size="sm" />
              </span>
            </AlertTitle>
            <AlertDescription>
              {saved.name} fica no perfil. Voltar a “Fundar o meu partido” o traz de volta.
            </AlertDescription>
          </Alert>
        )}
      </div>

      <PreparationFooter
        note={
          savedSimulation
            ? "Travado com partida salva selecionada."
            : "Fica no seu perfil: a contribuição. Só nesta sala: o partido em que você entra."
        }
        saving={autosave.saving}
        error={autosave.error}
        incomplete={autosave.incomplete}
        onRetry={autosave.retry}
        onClose={onClose}
      />
    </div>
  );
}

type PartyCardProps = {
  party: PlayerPreparation;
  members: string[];
  humans: RoomPlayer[];
  /** "here": o jogador já está neste partido; "entering": escolhido, entrando */
  state: "here" | "entering" | null;
  onPick: () => void;
};

function PartyCard({ party, members, humans, state, onPick }: PartyCardProps) {
  if (!party.party) return null;
  const colorOf = (nickname: string) => humans.find((human) => human.nickname === nickname)?.color ?? "";
  const shown = members.slice(0, MEMBERS_SHOWN);
  return (
    <button
      type="button"
      role="radio"
      aria-checked={state !== null}
      onClick={onPick}
      className={cn(
        "grid content-start gap-2.5 rounded-lg border bg-card p-3.5 text-left transition-colors outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
        state !== null ? "border-primary ring-1 ring-primary" : "hover:border-input",
      )}
    >
      <div className="flex items-start gap-2.5">
        <PartyMark abbr={party.party.abbr} color={party.party.color} size="lg" />
        <div className="grid min-w-0 flex-1 gap-0.5">
          <b className="truncate text-sm font-semibold" title={party.party.name}>
            {party.party.name}
          </b>
          <span className="text-xs text-muted-foreground">fundado por {party.nickname}</span>
        </div>
        {state && (
          <Badge variant={state === "here" ? "success" : "info"} size="sm">
            {state === "here" ? "você está aqui" : "você entra"}
          </Badge>
        )}
      </div>
      <ValueChips values={party.party.flags} />
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-[12.5px]">
        <dt className="text-muted-foreground">Candidato</dt>
        <dd className="truncate">{party.candidate ?? party.nickname}</dd>
        <dt className="text-muted-foreground">Vice</dt>
        <dd className="truncate">{party.vice ? `${party.vice} · aceito` : "a definir"}</dd>
        <dt className="text-muted-foreground">Filiados</dt>
        <dd className="flex items-center gap-1">
          {members.length === 0 ? (
            <span className="text-muted-foreground">nenhum ainda</span>
          ) : (
            <>
              {shown.map((member) => (
                <PlayerAvatar key={member} nickname={member} color={colorOf(member)} size="sm" />
              ))}
              {members.length > MEMBERS_SHOWN && (
                <span className="text-xs text-muted-foreground">+{members.length - MEMBERS_SHOWN}</span>
              )}
              {members.length <= 3 && <span className="truncate text-muted-foreground">{members.join(", ")}</span>}
            </>
          )}
        </dd>
      </dl>
    </button>
  );
}
