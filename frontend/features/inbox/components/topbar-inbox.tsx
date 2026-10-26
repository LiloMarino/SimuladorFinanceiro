import { useState } from "react";
import { Mail } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { InboxEntry, SimulationInfo } from "@/types";
import { useMarkInboxEntryRead } from "../hooks/mutations/useMarkInboxEntryRead";
import { useMarkInboxRead } from "../hooks/mutations/useMarkInboxRead";
import { useInbox } from "../hooks/queries/useInbox";
import { entryTitle } from "../lib/inbox";
import { InboxSheet } from "./inbox-sheet";

type TopbarInboxProps = {
  simulationId: NonNullable<SimulationInfo["simulation"]>["id"];
};

/** O envelope da barra da partida, com as não lidas, que abre a caixa de entrada. */
export function TopbarInbox({ simulationId }: TopbarInboxProps) {
  const { data: inbox } = useInbox(simulationId);
  const markRead = useMarkInboxEntryRead(simulationId);
  const markAllRead = useMarkInboxRead(simulationId);
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState<InboxEntry["id"] | null>(null);
  const unread = inbox?.unread ?? 0;

  // Abrir a entrada é lê-la; a da sala inteira fica como está
  const openEntry = (entry: InboxEntry) => {
    setExpanded(entry.id);
    if (!entry.read && !entry.room) markRead.mutate(entry.id);
  };

  const toggle = (entry: InboxEntry) => {
    if (entry.id === expanded) setExpanded(null);
    else openEntry(entry);
  };

  // A entrada nova avisa sem pausar a partida, com o atalho para lê-la
  useRealtime("inbox_entry", (entry) => {
    toast.info(entryTitle(entry.content), {
      description: "Chegou na sua caixa de entrada",
      action: {
        label: "Abrir",
        onClick: () => {
          setOpen(true);
          openEntry(entry);
        },
      },
    });
  });

  return (
    <>
      <span className="relative">
        <Button
          variant="outline"
          size="icon"
          aria-label={unread > 0 ? `Caixa de entrada, ${unread} não lidas` : "Caixa de entrada"}
          onClick={() => setOpen(true)}
        >
          <Mail />
        </Button>
        {unread > 0 && (
          <Badge size="sm" numeric className="pointer-events-none absolute -top-1.5 -right-1.5">
            {unread}
          </Badge>
        )}
      </span>
      <InboxSheet
        open={open}
        onOpenChange={setOpen}
        inbox={inbox}
        expanded={expanded}
        onToggle={toggle}
        onReadAll={() => markAllRead.mutate()}
      />
    </>
  );
}
