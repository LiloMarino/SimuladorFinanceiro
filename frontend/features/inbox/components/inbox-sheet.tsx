import { CalendarRange, ChevronDown, FileText, Inbox as InboxIcon } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/shared/components/ui/sheet";
import { cn } from "@/shared/lib/utils";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { Inbox, InboxEntry } from "@/types";
import { entryTitle } from "../lib/inbox";
import { MonthSummaryView } from "./month-summary";
import { YearReviewView } from "./year-review";

type InboxSheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  inbox: Inbox | undefined;
  expanded: InboxEntry["id"] | null;
  onToggle: (entry: InboxEntry) => void;
  onReadAll: () => void;
};

/** O painel lateral da caixa de entrada: as entradas por data, abertas uma por vez. */
export function InboxSheet({ open, onOpenChange, inbox, expanded, onToggle, onReadAll }: InboxSheetProps) {
  const entries = inbox?.entries ?? [];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent size="lg">
        {/* Cabeçalho */}
        <SheetHeader>
          <SheetTitle>Caixa de entrada</SheetTitle>
          <SheetDescription>
            O resumo de cada mês chega na virada do mês, e a retrospectiva do ano na virada do ano.
          </SheetDescription>
          {(inbox?.unread ?? 0) > 0 && (
            <Button variant="link" size="xs" className="self-start" onClick={onReadAll}>
              Marcar todas como lidas
            </Button>
          )}
        </SheetHeader>

        {/* Entradas */}
        <div className="grid content-start gap-2 overflow-y-auto px-6 py-4">
          {entries.length === 0 ? (
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <InboxIcon />
                </EmptyMedia>
                <EmptyTitle>Nada por aqui ainda</EmptyTitle>
                <EmptyDescription>O resumo do primeiro mês chega no primeiro pregão do mês seguinte.</EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            entries.map((entry) => (
              <InboxEntryCard
                key={entry.id}
                entry={entry}
                open={entry.id === expanded}
                onToggle={() => onToggle(entry)}
              />
            ))
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

type InboxEntryCardProps = {
  entry: InboxEntry;
  open: boolean;
  onToggle: () => void;
};

function InboxEntryCard({ entry, open, onToggle }: InboxEntryCardProps) {
  const content = entry.content;
  const Icon = content.kind === "YEAR_REVIEW" ? CalendarRange : FileText;

  return (
    <article className={cn("rounded-lg border border-border bg-card", !entry.read && "border-primary/40")}>
      <button
        type="button"
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-3.5 py-3 text-left"
        onClick={onToggle}
      >
        <Icon className="size-4 shrink-0 text-muted-foreground" />
        <span className="grid min-w-0 flex-1">
          <span className={cn("truncate text-sm", entry.read ? "font-medium" : "font-semibold")}>
            {entryTitle(content)}
          </span>
          <span className="text-xs text-muted-foreground">{displayIsoDate(entry.game_date)}</span>
        </span>
        {!entry.read && <span aria-label="Não lida" className="size-2 shrink-0 rounded-full bg-primary" />}
        <ChevronDown
          className={cn("size-4 shrink-0 text-muted-foreground transition-transform", open && "rotate-180")}
        />
      </button>
      {open && (
        <div className="border-t border-border px-3.5 py-3">
          {content.kind === "YEAR_REVIEW" ? (
            <YearReviewView review={content} />
          ) : (
            <MonthSummaryView summary={content} />
          )}
        </div>
      )}
    </article>
  );
}
