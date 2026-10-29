import { Siren } from "lucide-react";
import { useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";
import { outlookLabel } from "../lib/house";
import { VoteDialog } from "./vote-dialog";

type ImpeachmentRequestCardProps = { request: NonNullable<GovernmentPanel["congress"]["impeachment_request"]> };

/** O pedido de impeachment aberto: a casa vota no dia marcado e 68 votos Sim tiram o presidente. */
export function ImpeachmentRequestCard({ request }: ImpeachmentRequestCardProps) {
  const [open, setOpen] = useState(false);
  const { vote } = request;
  const president = request.president ?? "o presidente";

  return (
    <>
      <Alert variant="destructive">
        <Siren />
        <AlertTitle>Pedido de impeachment aberto · a casa vota em {displayDayMonth(request.vote_day)}</AlertTitle>
        <AlertDescription>
          <span className="grid gap-2">
            <span>
              O governo fechou meses seguidos abaixo do piso de aprovação. Para tirar {president}, {vote.needed} das 101
              cadeiras precisam votar Sim. {outlookLabel(vote)}.
            </span>
            <Button size="xs" variant="outline" className="justify-self-start" onClick={() => setOpen(true)}>
              Ver a votação
            </Button>
          </span>
        </AlertDescription>
      </Alert>
      <VoteDialog
        open={open}
        onOpenChange={setOpen}
        title="Pedido de impeachment"
        description={`Aberto em ${displayDayMonth(request.opened)} · a casa vota em ${displayDayMonth(request.vote_day)} · ${vote.needed} votos Sim tiram ${president}`}
        vote={vote}
        measureId={null}
        subject="o impeachment"
      />
    </>
  );
}
