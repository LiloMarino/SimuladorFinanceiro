import { Gavel, Lock, Megaphone, TrendingDown, TriangleAlert } from "lucide-react";
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
import { Skeleton } from "@/shared/components/ui/skeleton";
import { STATE_LEVER_LABEL } from "@/shared/lib/state-lever";
import {
  displayDayMonth,
  displayMoneyLarge,
  displayMonthSlashYear,
  displayNumber,
  displayPercent,
} from "@/shared/lib/utils/display";
import type { StateCompany } from "@/types";
import { useProposeMeasure } from "../../hooks/mutations/useProposeMeasure";
import { useMeasurePreview } from "../../hooks/queries/useMeasurePreview";
import { FAIR_VALUE } from "../../lib/government-metrics";
import { companyValue, unitPrice } from "../../lib/state-companies";
import { MeasureBudgetEffect } from "../measure-budget-effect";

type PrivatizeDialogProps = {
  company: StateCompany;
  /** Quantos pregões a oferta fica aberta à sala, como o painel entrega */
  offerSessions: number;
  onClose: () => void;
};

type FactProps = { label: React.ReactNode; children: React.ReactNode };

function Fact({ label, children }: FactProps) {
  return (
    <>
      <dt className="flex items-center gap-1.5 text-muted-foreground">{label}</dt>
      <dd className="text-right font-mono font-semibold">{children}</dd>
    </>
  );
}

/** Privatizar uma estatal: à esquerda a medida que vai ao Congresso, à direita a oferta pública que a sala verá se ela passar. */
export function PrivatizeDialog({ company, offerSessions, onClose }: PrivatizeDialogProps) {
  const propose = useProposeMeasure();
  const preview = useMeasurePreview({ kind: "PRIVATIZE_STATE_COMPANY", ticker: company.ticker });
  const data = preview.data;

  const paid = company.invested === null ? null : Number(company.invested);
  const proceeds = Number(company.government_value);
  const gap = paid === null ? null : proceeds - paid;
  const offered = Math.floor(company.shares * Number(company.government_share));

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-230">
        <DialogHeader variant="divided">
          <DialogTitle>Privatizar a {company.name}</DialogTitle>
          <DialogDescription>
            {company.ticker}
            {company.lever && ` · ${STATE_LEVER_LABEL[company.lever].toLowerCase()}`}
            {company.founded_on && ` · fundada em ${displayMonthSlashYear(company.founded_on)}`}. Vai como medida ao
            Congresso e, aprovada, abre uma oferta pública de {offerSessions} pregões para a sala toda.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-5 md:grid-cols-2">
            {/* A medida do presidente */}
            <section className="grid content-start gap-3.5">
              <h3 className="text-[13px] font-semibold text-muted-foreground">Presidente · a medida</h3>
              <dl className="grid grid-cols-[1fr_auto] gap-x-3 gap-y-2 text-[13px]">
                <Fact label="Valor da empresa">{displayMoneyLarge(companyValue(company))}</Fact>
                <Fact
                  label={
                    <>
                      Valor justo
                      <MetricHint metric={FAIR_VALUE} />
                    </>
                  }
                >
                  {unitPrice(company.fair_price)} contra {unitPrice(company.price)} na bolsa
                </Fact>
                <Fact label={`Fatia do governo à venda (${displayPercent(company.government_share, 0)})`}>
                  {displayMoneyLarge(proceeds)}
                </Fact>
                {paid !== null && <Fact label="Pago na fundação">{displayMoneyLarge(paid)}</Fact>}
              </dl>

              {gap !== null && (
                <Alert variant={gap < 0 ? "destructive" : "success"}>
                  <TrendingDown />
                  <AlertDescription>
                    <b className="font-semibold">
                      {gap < 0 ? "Prejuízo" : "Ganho"} de {displayMoneyLarge(Math.abs(gap))}.
                    </b>{" "}
                    {gap < 0
                      ? `A estatal vale menos do que o governo pagou: a venda arrecada ${displayMoneyLarge(proceeds)} para abater uma dívida de ${displayMoneyLarge(paid ?? 0)}.`
                      : `A estatal vale mais do que o governo pagou: a venda arrecada ${displayMoneyLarge(proceeds)} para abater a dívida de ${displayMoneyLarge(paid ?? 0)}.`}
                  </AlertDescription>
                </Alert>
              )}

              {data ? (
                <MeasureBudgetEffect effect={data.budget} />
              ) : preview.isError ? (
                <Alert variant="destructive">
                  <TriangleAlert />
                  <AlertTitle>Não deu para estimar a venda</AlertTitle>
                  <AlertDescription>{preview.error.message}</AlertDescription>
                </Alert>
              ) : (
                <Skeleton className="h-40 w-full" />
              )}

              <div className="grid gap-2 text-[13px]">
                <span className="font-semibold">Aprovada, acontece isto</span>
                <ul className="grid gap-2">
                  <li className="flex items-start gap-2">
                    <Megaphone className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                    Oferta aberta à sala por {offerSessions} pregões, ao valor justo. O formador do jogo compra o que
                    sobrar.
                  </li>
                  {company.origin === "FOUNDED" && (
                    <li className="flex items-start gap-2">
                      <TrendingDown className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                      A parte permanente do PIB que ela dava sai com a venda.
                    </li>
                  )}
                  <li className="flex items-start gap-2">
                    <Lock className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                    Até a votação, o controle e os dividendos dela ficam travados como estão.
                  </li>
                </ul>
              </div>
            </section>

            {/* A oferta pública */}
            <section className="grid content-start gap-3.5">
              <h3 className="text-[13px] font-semibold text-muted-foreground">
                Todos os jogadores · aprovada, a oferta aparece na Renda Variável e no Jornal
              </h3>
              <div className="grid gap-3 rounded-xl border p-4 text-[13px]">
                <h4 className="text-[15px] font-semibold">Oferta pública da {company.ticker}</h4>
                <p className="text-muted-foreground">
                  O governo vende os {displayPercent(company.government_share, 0)} da {company.name}. As reservas ficam
                  abertas por {offerSessions} pregões depois da aprovação.
                </p>
                <dl className="grid grid-cols-[1fr_auto] gap-x-3 gap-y-2 rounded-lg bg-subtle p-3">
                  <Fact label="Preço da oferta (valor justo)">{unitPrice(company.fair_price)}</Fact>
                  <Fact label="Ações à venda">{displayNumber(offered, 0)}</Fact>
                  <Fact label="Preço na bolsa hoje">{unitPrice(company.price)}</Fact>
                </dl>
                <p className="text-xs text-muted-foreground">
                  Cada jogador reserva as ações que quiser; as reservas saem do caixa no fim da oferta.
                </p>
              </div>
            </section>
          </div>

          {propose.isError && (
            <Alert variant="destructive" className="mt-4">
              <TriangleAlert />
              <AlertTitle>Não deu para enviar a medida</AlertTitle>
              <AlertDescription>{propose.error.message}</AlertDescription>
            </Alert>
          )}
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          {data && (
            <span className="mr-auto flex items-center gap-1.5 text-xs text-muted-foreground">
              <Gavel className="size-3.5" />
              Vota em {displayDayMonth(data.vote_date)}
            </span>
          )}
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            disabled={propose.isPending}
            onClick={() =>
              propose.mutate({ kind: "PRIVATIZE_STATE_COMPANY", ticker: company.ticker }, { onSuccess: onClose })
            }
          >
            Enviar ao Congresso
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
