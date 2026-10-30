import { TriangleAlert } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { CongressBase } from "@/types";
import { useBase } from "../hooks/queries/useBase";
import { useDealDialog } from "../hooks/useDealDialog";
import { monthlyLabel } from "../lib/base";

/** O aviso de que o governo espera a resposta do líder sobre a base; a aba Contas e a aba Congresso o mostram. */
export function ProposalNotice({ base }: { base: CongressBase }) {
  const { setOpen: openProposal } = useDealDialog();
  const proposal = base.my_proposal;

  if (!proposal || proposal.answer_by === null) return null;
  return (
    <Alert variant="warning">
      <TriangleAlert />
      <AlertTitle>
        O governo {base.president} espera sua resposta sobre a base · até {displayDayMonth(proposal.answer_by)}
      </AlertTitle>
      <AlertDescription>
        Emenda de {monthlyLabel(proposal.monthly)} por mês ao {proposal.abbr}, por {base.term_months} meses, em troca de
        orientar Sim.
      </AlertDescription>
      <AlertAction>
        <Button size="xs" onClick={() => openProposal(true)}>
          Ver a proposta
        </Button>
      </AlertAction>
    </Alert>
  );
}

/** O mesmo aviso fora da aba Contas: lê a base sozinho e some sem proposta esperando. */
export function BaseProposalNotice() {
  const { data: base } = useBase();

  return base ? <ProposalNotice base={base} /> : null;
}
