import { useState } from "react";
import { Bot, CalendarRange, CircleCheck, Handshake, TrendingUp, TriangleAlert, Users, Wallet } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Kpi } from "@/shared/components/kpi";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { CongressBase, DealPreview } from "@/types";
import { useProposeDeal } from "../hooks/mutations/useProposeDeal";
import { useDealPreview } from "../hooks/queries/useDealPreview";
import { baseOutlook, baseSeats, blocStatus, groupsLabel, monthlyLabel, yearShare } from "../lib/base";
import { AMENDMENTS } from "../lib/government-metrics";
import { blocColor } from "../lib/house";
import { Hemicycle } from "./hemicycle";
import { PartyMark } from "./party-mark";

type NegotiateDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  base: CongressBase;
  /** A bancada já escolhida ao abrir, como na renovação de um acordo que acaba */
  initialKey?: number | null;
};

/** Negociar apoio: o presidente clica numa bancada do hemiciclo, vê o preço e o efeito, e propõe. */
export function NegotiateDialog({ open, onOpenChange, base, initialKey = null }: NegotiateDialogProps) {
  const [selectedKey, setSelectedKey] = useState<number | null>(initialKey);
  const { data: preview, isPlaceholderData } = useDealPreview(selectedKey);
  const propose = useProposeDeal();
  const selectable = base.blocs.filter((bloc) => !bloc.governing);
  const chosen = preview && preview.bloc_key === selectedKey ? preview : null;

  const send = () =>
    selectedKey !== null && propose.mutate({ bloc_key: selectedKey }, { onSuccess: () => onOpenChange(false) });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-245">
        <DialogHeader variant="divided">
          <DialogTitle>Negociar apoio no Congresso</DialogTitle>
          <DialogDescription>
            Clique numa bancada para propor. O aliado orienta Sim em tudo o que o governo propuser, por{" "}
            {base.term_months} meses, em troca de uma emenda mensal.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-6 lg:grid-cols-[minmax(0,520px)_minmax(0,1fr)]">
            {/* Hemiciclo para escolher a bancada */}
            <div className="grid content-start justify-items-center gap-3">
              <Hemicycle
                seats={baseSeats(base.blocs, selectedKey)}
                width={520}
                label="Hemiciclo da base: clique numa bancada para propor"
                onSelect={(key) => selectable.some((bloc) => bloc.key === key) && setSelectedKey(key)}
              />
              <div className="flex flex-wrap justify-center gap-1.5">
                {selectable.map((bloc) => (
                  <button
                    key={bloc.key}
                    type="button"
                    aria-pressed={bloc.key === selectedKey}
                    onClick={() => setSelectedKey(bloc.key)}
                    className={cn(
                      "inline-flex h-7 items-center gap-1.5 rounded-full border px-2.5 text-xs font-medium",
                      bloc.key === selectedKey ? "border-primary bg-info-soft text-info" : "bg-card hover:bg-subtle",
                    )}
                  >
                    <PartyMark abbr={bloc.abbr} color={blocColor(bloc)} size="sm" />
                    {bloc.seats}
                    {blocStatus(bloc) === "in_base" && " · na base"}
                    {blocStatus(bloc) === "pending" && " · esperando"}
                  </button>
                ))}
              </div>
              <div className="flex flex-wrap justify-center gap-x-3.5 gap-y-1 text-xs text-muted-foreground">
                <span>cheia: na base</span>
                <span>anel: entra com a proposta</span>
                <span>clara: fora da base</span>
              </div>
            </div>

            {/* A proposta à bancada escolhida */}
            <div className={cn("grid min-w-0 content-start gap-3.5", isPlaceholderData && "opacity-60")}>
              {chosen ? (
                <ProposalDetail preview={chosen} base={base} />
              ) : (
                <div className="grid justify-items-center gap-2 rounded-xl border border-dashed p-8 text-center">
                  <Handshake className="size-6 text-muted-foreground" />
                  <b>Escolha uma bancada</b>
                  <span className="text-[13px] text-muted-foreground">
                    O preço, o efeito na base e na dívida aparecem aqui antes de você propor.
                  </span>
                </div>
              )}
            </div>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-between">
          <span className="text-xs text-muted-foreground">
            Cada cadeira custa 0,005% do PIB por ano; o centrão cobra 1,5 vez. Partido do computador responde no pregão
            seguinte; o de jogador tem {base.answer_days} dias.
          </span>
          <span className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button disabled={!chosen || chosen.blocker !== null || propose.isPending} onClick={send}>
              {chosen ? `Propor ao ${chosen.abbr} · ${monthlyLabel(chosen.monthly)} por mês` : "Propor"}
            </Button>
          </span>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function ProposalDetail({ preview, base }: { preview: DealPreview; base: CongressBase }) {
  const governing = base.governing_abbr ?? "governo";
  const who = preview.is_computer ? "computador" : "jogador";
  const description = [who, `${preview.seats} cadeiras`, preview.leader ? `líder ${preview.leader}` : null]
    .filter(Boolean)
    .join(" · ");
  const seatPrice = preview.centrao ? "× 0,0075% (1,5 vez)" : "× 0,005%";

  return (
    <>
      <div className="flex items-center gap-2.5">
        <PartyMark abbr={preview.abbr} color={blocColor(preview)} size="lg" />
        <span className="grid">
          <b>{preview.name}</b>
          <span className="text-xs text-muted-foreground">{description}</span>
        </span>
      </div>

      <Kpi
        label={
          <>
            {AMENDMENTS.label}
            <MetricHint metric={AMENDMENTS} />
          </>
        }
        value={
          <>
            {monthlyLabel(preview.monthly)} <span className="text-[13px] font-normal text-muted-foreground">/mês</span>
          </>
        }
        note={`${yearShare(preview.ratio)} do PIB por ano · ${preview.seats} cadeiras ${seatPrice}`}
      />

      {preview.blocker ? (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertTitle>Ainda não dá para propor</AlertTitle>
          <AlertDescription>{preview.blocker}</AlertDescription>
        </Alert>
      ) : preview.is_computer ? (
        <Alert variant={preview.likely ? "success" : "warning"}>
          <Bot />
          <AlertTitle>{preview.likely ? "Deve aceitar" : "Deve recusar"}</AlertTitle>
          <AlertDescription>
            {preview.centrao
              ? "O centrão aceita qualquer governo que pague."
              : `${preview.shared_flags} dos 3 valores em comum com o governo${preview.likely ? "" : ": ela pede ao menos 2"}.`}
          </AlertDescription>
        </Alert>
      ) : (
        <Alert variant="info">
          <Users />
          <AlertTitle>Partido de jogador: {preview.leader ?? "o líder"} decide</AlertTitle>
          <AlertDescription>
            Ele tem {base.answer_days} dias para responder; sem resposta, conta como recusa.
          </AlertDescription>
        </Alert>
      )}

      <ul className="grid rounded-lg border px-3 py-1 text-[13px]">
        <Line icon={CalendarRange}>
          {displayDayMonth(preview.start)} a {displayDayMonth(preview.end)}; acaba antes, sem quebra, se um novo
          Congresso tomar posse.
        </Line>
        <Line icon={Wallet}>
          Gasto +{yearShare(preview.ratio)} do PIB por ano
          {preview.debt_before !== null && preview.debt_after !== null && preview.debt_end && (
            <>
              ; a dívida em {displayDayMonth(preview.debt_end)} vai de{" "}
              <b className="font-mono">{displayPercent(preview.debt_before, 1)}</b> para{" "}
              <b className="font-mono">{displayPercent(preview.debt_after, 1)}</b>.
            </>
          )}
        </Line>
        <Line icon={CircleCheck}>
          Base de <b className="font-mono">{preview.base_before}</b> para{" "}
          <b className="font-mono">{preview.base_after}</b> cadeiras:{" "}
          {baseOutlook(preview.base_after, base.majority, base.impeachment_votes)}.
        </Line>
        <Line icon={TrendingUp}>
          {groupsLabel(preview.ally_groups)} sobem o apoio ao {preview.abbr}, cerca de +1 ponto por mês. Romper ou parar
          de pagar: esses grupos somam rejeição ao {governing}.
        </Line>
      </ul>
    </>
  );
}

function Line({ icon: Icon, children }: { icon: typeof Wallet; children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2.5 py-2">
      <Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
      <span>{children}</span>
    </li>
  );
}
