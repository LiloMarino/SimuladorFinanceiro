import { Check, TriangleAlert, X } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { outlook, outlookLabel, resultLabel, type Vote, voteSeats } from "../lib/house";
import { GuideTile } from "./guide-tile";
import { Hemicycle } from "./hemicycle";
import { VoteTable } from "./vote-table";

type VoteDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Título da medida, ou do pedido de impeachment */
  title: string;
  /** A linha de contexto: quem propôs, quando a casa vota, quando vale */
  description: string;
  vote: Vote;
  /** A medida votada; nulo é o pedido de impeachment */
  measureId: number | null;
  /** O que a votação decide, na frase da causa: "a medida" */
  subject: string;
  /** Quando já votada: se passou */
  approved?: boolean | undefined;
  mineKey?: number | undefined;
};

/** O painel de uma votação: o hemiciclo, a tabela das bancadas e, para o líder, a orientação. */
export function VoteDialog({
  open,
  onOpenChange,
  title,
  description,
  vote,
  measureId,
  subject,
  approved,
  mineKey,
}: VoteDialogProps) {
  const voted = vote.yes !== null;
  const mine = vote.guide ? vote.blocs.find((bloc) => bloc.key === vote.guide?.bloc_key) : undefined;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* O diálogo abre sem foco em nenhum controle: a tabela começa na primeira coluna e nenhuma dica abre sozinha */}
      <DialogContent initialFocus={false} className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-250">
        <DialogHeader variant="divided">
          <div className="flex flex-wrap items-center justify-between gap-3 pr-8">
            <DialogTitle>{title}</DialogTitle>
            {voted ? (
              <Badge variant={approved ? "success" : "destructive"}>
                {approved ? <Check /> : <X />}
                {resultLabel({ yes: vote.yes ?? 0, no: vote.no ?? 0 }, !!approved)}
              </Badge>
            ) : (
              <Badge variant={{ passes: "success", falls: "destructive", open: "warning" }[outlook(vote)] as "success"}>
                {outlookLabel(vote)}
              </Badge>
            )}
          </div>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-5 lg:grid-cols-[420px_minmax(0,1fr)]">
            {/* Hemiciclo da votação */}
            <div className="grid content-start justify-items-center gap-2.5">
              <Hemicycle seats={voteSeats(vote)} label={`Hemiciclo da votação, ${vote.needed} votos Sim para passar`} />
              <div className="flex flex-wrap gap-x-3.5 gap-y-1.5 text-xs text-muted-foreground">
                <Legend tone="solid" label={voted ? "cheia: votou Sim" : "cheia: Sim pela orientação"} />
                <Legend tone="light" label={voted ? "clara: votou Não" : "clara: Não"} />
              </div>
              <span className="text-xs text-muted-foreground">
                {voted ? "Com anel: votou contra a orientação do líder" : "Com anel: pode votar contra a orientação"}
              </span>
            </div>

            {/* Bancadas e orientação do líder */}
            <div className="grid min-w-0 content-start gap-3.5">
              <VoteTable vote={vote} subject={subject} mineKey={mineKey ?? vote.guide?.bloc_key} />
              {voted && (vote.defected ?? 0) > 0 && (
                <Alert variant="warning">
                  <TriangleAlert />
                  <AlertTitle>
                    {vote.defected} {vote.defected === 1 ? "deputado votou" : "deputados votaram"} contra a orientação
                  </AlertTitle>
                  <AlertDescription>
                    {vote.blocs
                      .filter((bloc) => (bloc.defected ?? 0) > 0)
                      .map((bloc) => `${bloc.defected} do ${bloc.abbr}`)
                      .join(", ")}{" "}
                    votaram contra o líder.
                  </AlertDescription>
                </Alert>
              )}
              {vote.guide && mine && (
                <GuideTile guide={vote.guide} measureId={measureId} current={mine.orientation} subject={subject} />
              )}
            </div>
          </div>
        </DialogBody>
      </DialogContent>
    </Dialog>
  );
}

function Legend({ tone, label }: { tone: "solid" | "light"; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <i
        className="inline-block size-2.5 rounded-full bg-foreground"
        style={{ opacity: tone === "light" ? 0.28 : 1 }}
      />
      {label}
    </span>
  );
}
