import type { GovernmentPanel } from "@/types";
import { HouseCard } from "./house-card";
import { BaseProposalNotice } from "./proposal-notice";
import { ImpeachmentRequestCard } from "./impeachment-request-card";
import { QueueCard } from "./queue-card";
import { VoteHistoryCard } from "./vote-history-card";

/** A aba Congresso: o pedido de impeachment, a casa, a fila de medidas e as votações feitas. */
export function CongressTab({ panel }: { panel: GovernmentPanel }) {
  const { congress } = panel;

  return (
    <div className="grid gap-5 pt-3">
      <BaseProposalNotice />
      {congress.impeachment_request && <ImpeachmentRequestCard request={congress.impeachment_request} />}
      <HouseCard house={congress.house} />
      <QueueCard panel={panel} />
      <VoteHistoryCard history={congress.history} />
    </div>
  );
}
