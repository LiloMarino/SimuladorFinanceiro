import { CalendarClock, Hourglass, Megaphone } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { displayDayMonth, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, RunoffRace, RunoffTransfer } from "@/types";
import { useToday } from "../hooks/useToday";
import { undecidedNow, undecidedPointsText } from "../lib/runoff";
import { groupList } from "../lib/voters";

/** Confiança a partir da qual um grupo segue a indicação do partido que saiu. */
const TRUSTED = 0.5;

type RunoffNoticesProps = { panel: ElectionPanel; race: RunoffRace };

/** Os avisos públicos do 2º turno: a declaração de cada partido que saiu (ou a falta dela) e a véspera da votação. */
export function RunoffNotices({ panel, race }: RunoffNoticesProps) {
  const today = useToday(panel);
  const weights = new Map(panel.groups.map((group) => [group.group, group.weight]));
  const latest = race.polls.at(-1);
  const eve = today === panel.dates.donation_deadline;

  return (
    <>
      {eve && (
        <Alert variant="warning">
          <CalendarClock />
          <AlertTitle>Véspera do 2º turno</AlertTitle>
          <AlertDescription>
            Hoje é o último dia para ações, contribuições, doações e declarações de apoio. Amanhã,{" "}
            {displayShortDate(panel.dates.runoff)},{" "}
            {latest
              ? `os ${Math.round(Number(latest.undecided))} pontos indecisos que sobraram não votam.`
              : "quem continuar indeciso não vota."}
          </AlertDescription>
        </Alert>
      )}
      {race.transfers.map((transfer) => (
        <DeclarationNotice key={transfer.party_id} panel={panel} race={race} transfer={transfer} weights={weights} />
      ))}
    </>
  );
}

type DeclarationNoticeProps = {
  panel: ElectionPanel;
  race: RunoffRace;
  transfer: RunoffTransfer;
  weights: Map<string, string>;
};

function DeclarationNotice({ panel, race, transfer, weights }: DeclarationNoticeProps) {
  const party = panel.parties.find((candidate) => candidate.id === transfer.party_id);
  if (!party) return null;

  if (!transfer.declared) {
    // Quem pode declarar já tem o aviso com o botão; os demais acompanham a espera
    if (race.can_declare && panel.my_party?.party_id === party.id) return null;
    const leader = party.founder ? `${party.founder}, líder do ${party.abbr}, pode` : `O ${party.abbr} pode`;
    return (
      <Alert variant="info">
        <Hourglass />
        <AlertTitle>O {party.abbr} ainda não declarou apoio</AlertTitle>
        <AlertDescription>
          {leader} declarar até {displayDayMonth(panel.dates.donation_deadline)}. Enquanto não declara,{" "}
          {undecidedPointsText(undecidedNow(transfer, weights))}: quanto mais espera, mais deles as ações dos dois
          finalistas levam.
        </AlertDescription>
      </Alert>
    );
  }

  const declaration = race.declarations.find((item) => item.party_id === party.id);
  const endorsed = panel.parties.find((candidate) => candidate.id === transfer.endorsed_party_id);
  const who = declaration?.nickname ? `${declaration.nickname}, do ${party.abbr},` : `O ${party.abbr}`;
  const when = declaration ? ` em ${displayDayMonth(declaration.date)}` : "";
  const trusted = transfer.groups.filter((group) => Number(group.trust) >= TRUSTED).map((group) => group.group);

  return (
    <Alert variant="info">
      <Megaphone />
      <AlertTitle>
        {who} declarou {endorsed ? `apoio ao ${endorsed.abbr}` : "neutralidade"}
        {when}
      </AlertTitle>
      <AlertDescription>
        {endorsed
          ? `Os grupos que confiam no ${party.abbr} levam parte dos indecisos ao ${endorsed.abbr}${trusted.length > 0 ? `: ${groupList(trusted)}` : ""}. Vale até o 2º turno.`
          : `Os grupos que confiam no ${party.abbr} não recebem indicação: os indecisos deles ficam para as campanhas disputarem.`}
      </AlertDescription>
    </Alert>
  );
}
