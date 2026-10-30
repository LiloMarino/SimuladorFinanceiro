import { format, subMonths } from "date-fns";
import { Gavel } from "lucide-react";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/shared/components/ui/dialog";
import { parseLocalDate } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";
import { monthsSpan } from "../lib/approval";
import { monthYear } from "../lib/government";
import { PartyMark } from "./party-mark";

type ImpeachmentDialogProps = {
  /** O governo logo depois do impeachment; nulo mantém o diálogo fechado */
  panel: GovernmentPanel | null;
  onClose: () => void;
};

/** O impeachment, para todos: quem saiu, quem assume e o que muda nas carteiras. */
export function ImpeachmentDialog({ panel, onClose }: ImpeachmentDialogProps) {
  return (
    <Dialog open={!!panel?.last_impeachment} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-110">
        {panel?.last_impeachment && <ImpeachmentBody panel={panel} onClose={onClose} />}
      </DialogContent>
    </Dialog>
  );
}

/** A votação cai no mês seguinte ao último fechamento abaixo do piso. */
function lastClosing(voteDate: string) {
  return format(subMonths(parseLocalDate(voteDate), 1), "yyyy-MM-dd");
}

function ImpeachmentBody({ panel, onClose }: ImpeachmentDialogProps) {
  const impeachment = panel?.last_impeachment;
  if (!panel || !impeachment) return null;
  const { successor, months, floor, date, yes, no } = impeachment;
  const president = impeachment.president ?? "O presidente";
  const cause = `A aprovação fechou ${months} meses seguidos abaixo de ${floor}%, de ${monthsSpan(lastClosing(date), months)}, e a casa aprovou o impeachment por ${yes} a ${no}.`;
  const until = panel.term_end ? monthYear(panel.term_end) : "o fim do mandato";
  // Sem vice, assume o partido do computador com mais cadeiras: a bancada que agora governa
  const heir = successor ? undefined : panel.congress.house.blocs.find((bloc) => bloc.governing && bloc.is_computer);
  const heirName = panel.term?.president?.name;

  return (
    <div className="grid justify-items-start gap-2.5">
      <span className="inline-flex size-12 items-center justify-center rounded-xl bg-destructive-soft text-destructive">
        <Gavel className="size-5.5" />
      </span>
      <DialogTitle>
        {successor || heir
          ? `${president} sofreu impeachment; ${successor ?? heir?.abbr} assume`
          : `${president} sofreu impeachment`}
      </DialogTitle>
      <DialogDescription>
        {successor
          ? `${cause} ${successor} governa até ${until}, como vice: a carteira de ${successor} congela e a de ${president} volta a operar.`
          : heir
            ? `${cause} ${president} não tinha vice. Assume o partido do computador com mais cadeiras, ${heir.abbr} (${heir.seats}), até ${until}: ele propõe medidas pelos grupos de eleitores dele, e a casa vota como sempre. A carteira de ${president} volta a operar.`
            : `${cause} Não havia vice para assumir: um governo neutro do computador conduz o país, sem mudar impostos, até a eleição de ${monthYear(panel.next_election)}. A carteira de ${president} volta a operar.`}
      </DialogDescription>
      {successor ? (
        <div className="flex items-center gap-2">
          <PlayerAvatar nickname={president} size="sm" />
          <span className="text-muted-foreground">→</span>
          <PlayerAvatar nickname={successor} size="sm" />
          <b className="text-[13px]">Governo {successor}</b>
        </div>
      ) : heir ? (
        <div className="flex items-center gap-2.5 text-[13px]">
          <PartyMark abbr={heir.abbr} color={null} />
          <span>Governo {heirName ?? heir.abbr} · computador</span>
        </div>
      ) : (
        <Badge variant="secondary" className="h-7.5">
          <ExpansionEmblem expansion="government" size="xs" />
          Governo neutro do computador
        </Badge>
      )}
      <Button size="sm" onClick={onClose}>
        Entendi
      </Button>
    </div>
  );
}
