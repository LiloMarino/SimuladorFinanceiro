import { useState } from "react";
import { KeyValueRow } from "@/shared/components/key-value-row";
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
import { Spinner } from "@/shared/components/ui/spinner";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";
import { useContributeToFund } from "../hooks/mutations/useContributeToFund";
import { cashOf, contributionBody, contributionReady, picksValue, type StockPicks } from "../lib/fund-contribution";
import { foundingSummary } from "../lib/fund-math";
import { ContributionPicker } from "./contribution-picker";
import { useOperatingAsFund } from "../hooks/useOperatingAsFund";
import { PersonalAccountNotice } from "./personal-account-notice";

type ContributeDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fundId: number;
  fundName: string;
  /** O preço da cota em que a integralização é contada */
  quotaPrice: number;
};

type ContributeFormProps = Omit<ContributeDialogProps, "open" | "fundName"> & { portfolio: PortfolioState };

/** O formulário nasce a cada abertura do diálogo: caixa e ações começam vazios. */
function ContributeForm({ onOpenChange, fundId, quotaPrice, portfolio }: ContributeFormProps) {
  const [cashText, setCashText] = useState("");
  const [picks, setPicks] = useState<StockPicks>({});
  const contribute = useContributeToFund();

  const summary = foundingSummary(cashOf(cashText), picksValue(picks, portfolio.variable_income), quotaPrice);
  const ready =
    contributionReady(cashText, picks, portfolio.variable_income, Number(portfolio.cash)) && summary.quotas >= 1;

  const submit = () =>
    contribute.mutate({ fundId, request: contributionBody(cashText, picks) }, { onSuccess: () => onOpenChange(false) });

  return (
    <>
      <DialogBody>
        <ContributionPicker
          portfolio={portfolio}
          cashText={cashText}
          onCashChange={setCashText}
          picks={picks}
          onPicksChange={setPicks}
          idPrefix="contribute"
        />
        <div>
          <KeyValueRow label="Sai da sua carteira" value={displayMoney(summary.taken)} />
          <KeyValueRow label="Preço da cota" value={displayMoney(quotaPrice)} />
          <KeyValueRow label="Você recebe" value={`${displayQuantity(String(summary.quotas))} cotas`} total />
          <KeyValueRow label="Sobra, fica na gestora" value={displayMoney(summary.leftover)} />
        </div>
      </DialogBody>
      <DialogFooter variant="divided">
        <Button variant="outline" onClick={() => onOpenChange(false)}>
          Cancelar
        </Button>
        <Button variant="fund" disabled={!ready || contribute.isPending} onClick={submit}>
          {contribute.isPending && <Spinner />}
          Levar e receber {displayQuantity(String(summary.quotas))} cotas
        </Button>
      </DialogFooter>
    </>
  );
}

/** Levar da carteira: com a gestora fechada, o gestor leva caixa e ações em troca de cotas. */
export function ContributeDialog({ open, onOpenChange, fundId, fundName, quotaPrice }: ContributeDialogProps) {
  const operatingAsFund = useOperatingAsFund();
  const { data: portfolio } = usePortfolio({ enabled: open && !operatingAsFund });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Levar da carteira para {fundName}</DialogTitle>
          <DialogDescription>
            Caixa e ações da sua carteira viram cotas da gestora. Os títulos de renda fixa ficam de fora. Depois da
            primeira oferta pública, a gestora deixa de aceitar.
          </DialogDescription>
        </DialogHeader>
        {operatingAsFund ? (
          <DialogBody>
            <PersonalAccountNotice>
              O que você leva sai da sua carteira pessoal. Volte para ela para escolher caixa e ações.
            </PersonalAccountNotice>
          </DialogBody>
        ) : portfolio ? (
          <ContributeForm onOpenChange={onOpenChange} fundId={fundId} quotaPrice={quotaPrice} portfolio={portfolio} />
        ) : (
          <DialogBody>
            <Skeleton className="h-48" />
          </DialogBody>
        )}
      </DialogContent>
    </Dialog>
  );
}
