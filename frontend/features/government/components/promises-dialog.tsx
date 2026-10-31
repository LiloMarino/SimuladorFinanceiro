import { useState } from "react";
import { Info, Lock, Plus, RefreshCw, TriangleAlert, X } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
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
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { isConnectionFailure } from "@/shared/lib/models/ApiError";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { PromisesPanel, PromisesPreview, VoterGroupInfo } from "@/types";
import { useSetPromises } from "../hooks/mutations/useSetPromises";
import { usePromises } from "../hooks/queries/usePromises";
import { usePromisesPreview } from "../hooks/queries/usePromisesPreview";
import {
  PROMISE_BREACH,
  PROMISE_YIELD,
  type PromiseDraft,
  draftOf,
  isComplete,
  promiseKey,
  signedDecimal,
  toRequest,
  weightedSupport,
} from "../lib/promises";
import { VALUE_INFO } from "@/shared/lib/party-flags";
import { GROUP_INFO } from "../lib/voters";
import { PromiseEditor } from "./promise-editor";
import { SignedDecimal } from "./signed-decimal";
import { GroupIcon, ValueChip } from "./value-chip";

type PromisesDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  abbr: string;
  groups: VoterGroupInfo[];
};

/** As promessas da chapa: até 3 medidas que rendem apoio desde o anúncio e são cobradas no fim do mandato. */
export function PromisesDialog({ open, onOpenChange, abbr, groups }: PromisesDialogProps) {
  const query = usePromises(open);
  const panel = query.data;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-275">
        <DialogHeader variant="divided">
          <DialogTitle>Promessas da chapa do {abbr}</DialogTitle>
          <DialogDescription>
            {panel?.add_only
              ? `Entre os turnos a chapa acrescenta promessas, até ${panel.max_promises}. As já anunciadas não se retiram nem se trocam, e a nova rende desde o anúncio.`
              : "Até 3 medidas que o governo pode propor. A promessa rende apoio desde o anúncio e é cobrada no fim do mandato."}
          </DialogDescription>
        </DialogHeader>
        {panel ? (
          <PromisesForm panel={panel} groups={groups} onClose={() => onOpenChange(false)} />
        ) : query.isError ? (
          <DialogBody>
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>Não deu para carregar as promessas</AlertTitle>
              <AlertDescription>{query.error.message}</AlertDescription>
              <AlertAction>
                <Button size="sm" variant="outline" onClick={() => void query.refetch()}>
                  <RefreshCw />
                  Tentar de novo
                </Button>
              </AlertAction>
            </Alert>
          </DialogBody>
        ) : (
          <DialogBody>
            <div className="grid gap-3" aria-busy="true" aria-label="Carregando as promessas">
              <Skeleton className="h-16" />
              <Skeleton className="h-48" />
            </div>
          </DialogBody>
        )}
      </DialogContent>
    </Dialog>
  );
}

type PromisesFormProps = {
  panel: PromisesPanel;
  groups: VoterGroupInfo[];
  onClose: () => void;
};

function PromisesForm({ panel, groups, onClose }: PromisesFormProps) {
  const setPromises = useSetPromises();
  const initial = panel.promises.map(draftOf);
  const [drafts, setDrafts] = useState<PromiseDraft[]>(initial);
  const [selected, setSelected] = useState(0);

  const locked = !panel.open;
  // Entre os turnos as promessas já anunciadas ficam como estão; só entram novas
  const fixedCount = panel.add_only ? panel.promises.length : 0;
  const complete = drafts.filter((draft) => isComplete(draft, panel.options));
  const hasIncomplete = complete.length < drafts.length;
  const request = locked ? null : { promises: complete.map(toRequest) };
  const preview = usePromisesPreview(request);
  const data = preview.isError ? undefined : preview.data;
  // Com a lista mudada, a prévia em tela ainda é a da lista anterior até a nova chegar
  const recalculating = preview.isPlaceholderData;

  const current: PromiseDraft | undefined = drafts[selected];
  const taken = new Set(drafts.filter((_, index) => index !== selected).map((draft) => draft.kind));
  const previewOf = (draft: PromiseDraft) => data?.items.find((item) => promiseKey(item.promise) === promiseKey(draft));
  const changed = JSON.stringify(complete.map(toRequest)) !== JSON.stringify(initial.map(toRequest));
  const retreat = data?.totals.filter((row) => Number(row.retreat) > 0) ?? [];

  const update = (draft: PromiseDraft) =>
    setDrafts((list) => list.map((item, index) => (index === selected ? draft : item)));
  const add = () => {
    const option = panel.options.find((candidate) => !drafts.some((draft) => draft.kind === candidate.kind));
    if (!option) return;
    setDrafts((list) => [...list, { kind: option.kind, target: option.baseline, sector: null, segment: null }]);
    setSelected(drafts.length);
  };
  const remove = (index: number) => {
    setDrafts((list) => list.filter((_, position) => position !== index));
    setSelected(0);
  };

  return (
    <>
      <DialogBody>
        <div className="grid gap-4">
          {locked && (
            <Alert variant="muted">
              <Lock />
              <AlertTitle>{panel.closed_reason}</AlertTitle>
              <AlertDescription>
                {panel.add_only
                  ? "Até a votação do 2º turno, nada muda nas promessas."
                  : `As chapas fecham em ${displayDayMonth(panel.ticket_deadline)}. Até a eleição, nada muda nas promessas.`}
              </AlertDescription>
            </Alert>
          )}

          <div className="grid gap-6 md:grid-cols-[260px_minmax(0,1fr)]">
            {/* Lista de promessas */}
            <div className="grid content-start gap-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium">Promessas</span>
                <span className="font-mono text-muted-foreground">
                  {drafts.length} de {panel.max_promises}
                </span>
              </div>
              {drafts.map((draft, index) => {
                const item = previewOf(draft);
                const total = item ? weightedSupport(item.rows, groups) : null;
                return (
                  <div
                    key={promiseKey(draft)}
                    className={cn(
                      "flex items-start gap-2 rounded-lg border px-3 py-2",
                      index === selected && "border-primary bg-info-soft",
                    )}
                  >
                    <button
                      type="button"
                      className="grid min-w-0 flex-1 gap-1 text-left"
                      aria-current={index === selected}
                      onClick={() => setSelected(index)}
                    >
                      <b className="truncate text-[13px]" title={item?.promise.title}>
                        {item?.promise.title ?? "Defina o alvo"}
                      </b>
                      <span className={cn("text-xs text-muted-foreground", recalculating && "opacity-50")}>
                        {total === null ? "sem prévia" : "no total"}{" "}
                        {total !== null && (
                          <span
                            className={cn("font-mono font-semibold", total >= 0 ? "text-success" : "text-destructive")}
                          >
                            {signedDecimal(total)}
                          </span>
                        )}
                      </span>
                    </button>
                    {!locked && index >= fixedCount && (
                      <Button
                        size="icon-xs"
                        variant="ghost"
                        aria-label="Retirar promessa"
                        onClick={() => remove(index)}
                      >
                        <X />
                      </Button>
                    )}
                  </div>
                );
              })}
              {drafts.length === 0 && (
                <p className="rounded-lg bg-subtle px-3 py-2 text-xs leading-normal text-muted-foreground">
                  Sem promessa, a chapa não ganha nem arrisca nada com elas. Prometa até {panel.max_promises} medidas e
                  veja quanto cada uma rende em cada grupo.
                </p>
              )}
              {!locked && (
                <Button
                  size="sm"
                  variant="outline"
                  disabled={drafts.length >= panel.max_promises || hasIncomplete}
                  onClick={add}
                >
                  <Plus />
                  Adicionar promessa
                  <span className="ml-auto text-[11px] text-muted-foreground">no máximo {panel.max_promises}</span>
                </Button>
              )}
              <p className="grid gap-1 pt-1 text-xs leading-normal text-muted-foreground">
                Rendem desde o anúncio até o dia da eleição e não caem com o tempo.
                {data && drafts.length > 1 && (
                  <span className="flex justify-between">
                    <b className="text-foreground">As {drafts.length} juntas</b>
                    <span className="font-mono font-semibold">
                      {signedDecimal(data.items.reduce((sum, item) => sum + weightedSupport(item.rows, groups), 0))} no
                      total
                    </span>
                  </span>
                )}
              </p>
            </div>

            {/* Promessa em edição */}
            <div className="grid min-w-0 content-start gap-4">
              {current ? (
                <>
                  <PromiseEditor
                    draft={current}
                    panel={panel}
                    taken={taken}
                    disabled={locked || selected < fixedCount}
                    onChange={update}
                  />
                  {preview.isError &&
                    (isConnectionFailure(preview.error.status) ? (
                      <Alert variant="destructive">
                        <TriangleAlert />
                        <AlertTitle>Não deu para calcular o que as promessas rendem</AlertTitle>
                        <AlertDescription>{preview.error.message}</AlertDescription>
                        <AlertAction>
                          <Button size="sm" variant="outline" onClick={() => void preview.refetch()}>
                            <RefreshCw />
                            Tentar de novo
                          </Button>
                        </AlertAction>
                      </Alert>
                    ) : (
                      <Alert variant="destructive">
                        <TriangleAlert />
                        <AlertTitle>Essa lista de promessas não dá para anunciar</AlertTitle>
                        <AlertDescription>{preview.error.message}</AlertDescription>
                      </Alert>
                    ))}
                  {isComplete(current, panel.options) ? (
                    <PromiseEffects
                      item={previewOf(current)}
                      groups={groups}
                      abbr={panel.party_abbr}
                      stale={recalculating}
                    />
                  ) : (
                    <p className="text-xs text-muted-foreground">
                      Defina o alvo para ver o que a promessa faz em cada grupo.
                    </p>
                  )}
                </>
              ) : (
                <p className="rounded-lg bg-subtle px-3 py-6 text-center text-sm text-muted-foreground">
                  A chapa ainda não prometeu nada.
                </p>
              )}
            </div>
          </div>

          {retreat.length > 0 && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>Voltar atrás custa rejeição</AlertTitle>
              <AlertDescription>
                Retirar, trocar ou baixar o alvo de uma promessa já anunciada soma rejeição em quem queria a medida:{" "}
                {retreat.map((row) => `${GROUP_INFO[row.group].short} ${signedDecimal(row.retreat)}`).join(" · ")}. É
                metade do que custaria descumprir. Acrescentar promessa, até {panel.max_promises}, não custa nada.
              </AlertDescription>
            </Alert>
          )}

          {setPromises.isError && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>Não deu para anunciar as promessas</AlertTitle>
              <AlertDescription>{setPromises.error.message}</AlertDescription>
            </Alert>
          )}
        </div>
      </DialogBody>

      <DialogFooter variant="divided" className="sm:data-[variant=divided]:justify-end">
        <span className="mr-auto flex max-w-[620px] items-center gap-1.5 text-xs text-muted-foreground">
          <Info className="size-3.5 shrink-0" />
          {panel.add_only
            ? "No anúncio, a sala vê a promessa nova e ela passa a render no voto de cada grupo."
            : "No anúncio, a sala vê as promessas e elas passam a render. Depois dele, trocar, retirar ou baixar o alvo custa rejeição."}
        </span>
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button
          disabled={locked || hasIncomplete || preview.isError || recalculating || !changed || setPromises.isPending}
          onClick={() => request && setPromises.mutate(request, { onSuccess: onClose })}
        >
          {retreat.length > 0 ? "Anunciar e pagar o custo" : "Anunciar promessas"}
        </Button>
      </DialogFooter>
    </>
  );
}

type PromiseEffectsProps = {
  item: PromisesPreview["items"][number] | undefined;
  groups: VoterGroupInfo[];
  abbr: string;
  /** A prévia é a da lista anterior: números esmaecidos até a nova chegar */
  stale: boolean;
};

/** O que a promessa faz no perfil do partido e em cada grupo de eleitores. */
function PromiseEffects({ item, groups, abbr, stale }: PromiseEffectsProps) {
  if (!item) return null;
  const weights = new Map(groups.map((info) => [info.group, info.weight]));
  const total = weightedSupport(item.rows, groups);

  return (
    <div className={cn("grid gap-4", stale && "opacity-50")}>
      {item.values.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground">Move o perfil do {abbr}:</span>
          {item.values.map((move) => (
            <span key={move.value} className="inline-flex items-center gap-1">
              <ValueChip value={move.value} />
              <b className={cn("text-xs", Number(move.effect) > 0 ? "text-success" : "text-destructive")}>
                {Number(move.effect) > 0 ? "▲" : "▼"}
              </b>
              <span className="sr-only">{VALUE_INFO[move.value].label}</span>
            </span>
          ))}
        </div>
      )}

      <div className="grid gap-2">
        <div className="flex items-baseline justify-between gap-2">
          <b className="text-sm">O que a promessa faz em cada grupo</b>
          <Badge variant="secret" size="sm">
            Só o {abbr} vê estes números
          </Badge>
        </div>
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Grupo</TableHead>
                <TableHead>O grupo</TableHead>
                <TableHead>
                  <span className="inline-flex items-center gap-1">
                    {PROMISE_YIELD.label}
                    <MetricHint metric={PROMISE_YIELD} />
                  </span>
                </TableHead>
                <TableHead>
                  <span className="inline-flex items-center gap-1">
                    {PROMISE_BREACH.label}
                    <MetricHint metric={PROMISE_BREACH} />
                  </span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {item.rows.map((row) => {
                const support = Number(row.support);
                const reaction = row.wanted ? "quer" : support < 0 ? "não quer" : "tanto faz";
                return (
                  <TableRow key={row.group}>
                    <TableCell>
                      <span className="flex items-center gap-2.5">
                        <GroupIcon group={row.group} className="size-7" />
                        <span className="grid gap-px">
                          <b className="text-[13px] font-semibold">{GROUP_INFO[row.group].label}</b>
                          <span className="text-xs text-muted-foreground">
                            {displayPercent(weights.get(row.group) ?? 0, 0)} do eleitorado
                          </span>
                        </span>
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant={row.wanted ? "success" : support < 0 ? "destructive" : "secondary"} size="sm">
                        {reaction}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {support === 0 ? (
                        <span className="text-xs text-muted-foreground">a medida não pesa para o grupo</span>
                      ) : (
                        <span className="grid gap-px">
                          <b className={cn("font-mono text-[13px]", support > 0 ? "text-success" : "text-destructive")}>
                            {signedDecimal(support)}
                          </b>
                          <span className="text-[11px] text-muted-foreground">
                            {support > 0
                              ? `ganho de ${Number(row.support_full).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} × ${(1 - Number(row.rejection) / 100).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}, pela rejeição de ${Math.round(Number(row.rejection))}`
                              : "quem não quer tira cheio"}
                          </span>
                        </span>
                      )}
                    </TableCell>
                    <TableCell>
                      {row.wanted && Number(row.breach) > 0 ? (
                        <span className="text-xs">
                          <SignedDecimal value={row.breach} rising="bad" className="font-semibold" /> de rejeição
                        </span>
                      ) : (
                        <span className="text-faint-foreground">—</span>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
              <TableRow variant="group">
                <TableCell>
                  <span className="grid gap-px">
                    <b>No total</b>
                    <span className="text-xs text-muted-foreground">pelo peso de cada grupo</span>
                  </span>
                </TableCell>
                <TableCell colSpan={3}>
                  <span className="flex items-center gap-3 text-xs text-muted-foreground">
                    <b className={cn("font-mono text-[15px]", total >= 0 ? "text-success" : "text-destructive")}>
                      {signedDecimal(total)}
                    </b>
                    {total >= 0
                      ? "A promessa soma mais apoio do que tira, olhando o eleitorado inteiro."
                      : "A promessa tira mais apoio do que soma, olhando o eleitorado inteiro."}
                  </span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <span className="text-xs leading-normal text-muted-foreground">
          Num grupo, a promessa rende multiplicada por (1 − rejeição ÷ 100): quanto mais o grupo já rejeita o {abbr},
          menos acredita nela.
        </span>
      </div>
    </div>
  );
}
