import { CalendarClock, Vote } from "lucide-react";
import { useState } from "react";
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
import { Spinner } from "@/shared/components/ui/spinner";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { displayIsoDate, displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useProposeFeeIncrease } from "../hooks/mutations/useProposeFeeIncrease";
import { useSetFundFees } from "../hooks/mutations/useSetFundFees";
import { blockReason, feeTitle, optionOf } from "../lib/fund-assembly";
import { futureShareOf } from "../lib/fund-comanagers";
import { aboveWaterMark, feeToBody, feeToPoints, managementPerMonth, raisesFee, snapFee } from "../lib/fund-fees";
import { fundStage, netWorthOf } from "@/shared/lib/fund-view";
import { FeeControls } from "./fee-controls";

type FeesDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fund: FundDetails;
};

type Rules = { maxManagement: string; maxPerformance: string };

/** A marca d'água de hoje contra a cota de hoje: quanto falta ou quanto já passou. */
function WaterMarkToday({ fund }: { fund: FundDetails }) {
  const { high_water_mark: mark, high_water_mark_on: markDay } = fund.fees;
  if (mark === null || fund.nav === null) {
    return (
      <span className="mt-1.5 block">
        Ainda não há marca d&apos;água: a primeira performance se mede pela cota de R$ 100,00.
      </span>
    );
  }
  const above = aboveWaterMark(Number(fund.nav), Number(mark));

  return (
    <span className="mt-1.5 block">
      Hoje a marca d&apos;água é <b className="font-mono font-semibold text-foreground">{displayMoney(mark)}</b>
      {markDay && <> (de {displayIsoDate(markDay)})</>} e a cota vale{" "}
      <b className="font-mono font-semibold text-foreground">{displayMoney(fund.nav)}</b>:{" "}
      {above > 0
        ? `já passa ${displayMoney(above)} da marca, e só isso conta para a performance.`
        : "a performance só volta a contar quando a cota passar da marca."}
    </span>
  );
}

type RaiseNoteProps = { fund: FundDetails; management: number; performance: number };

/** O que o aumento pede: a votação dos cotistas, o prazo e quanto a administração rende a mais por mês. */
function RaiseNote({ fund, management, performance }: RaiseNoteProps) {
  const title = feeTitle({
    management_from: fund.management_fee,
    management_to: feeToBody(management),
    performance_from: fund.performance_fee,
    performance_to: feeToBody(performance),
  });
  const extra =
    managementPerMonth(netWorthOf(fund), management) -
    managementPerMonth(netWorthOf(fund), feeToPoints(fund.management_fee));
  const comanagers = fund.comanagers.filter((comanager) => comanager.status === "ACTIVE");
  const managerShare = 1 - comanagers.reduce((sum, comanager) => sum + futureShareOf(comanager), 0);
  const split = [
    `você (${displayPercent(managerShare, 0, { trim: true })})`,
    ...comanagers.map(
      (comanager) => `${comanager.nickname} (${displayPercent(futureShareOf(comanager), 0, { trim: true })})`,
    ),
  ];

  return (
    <Alert variant="info">
      <Vote />
      <AlertTitle>Subir a taxa vai à assembleia</AlertTitle>
      <AlertDescription>
        {title} tem 5 pregões de votação dos cotistas e, aprovado, vale no mês seguinte ao resultado.
        {extra > 0 && (
          <>
            {" "}
            Seriam cerca de {displayMoney(extra)} a mais por mês
            {comanagers.length > 0 ? `, divididos entre ${split.join(" e ")}` : ""}.
          </>
        )}{" "}
        Baixar vale no mês seguinte, sem votação.
      </AlertDescription>
    </Alert>
  );
}

type FeesFormProps = { fund: FundDetails; rules: Rules; onOpenChange: (open: boolean) => void };

/** O formulário nasce a cada abertura: parte das taxas em vigor, ou das pendentes quando já há mudança marcada. */
function FeesForm({ fund, rules, onOpenChange }: FeesFormProps) {
  const capManagement = feeToPoints(rules.maxManagement);
  const capPerformance = feeToPoints(rules.maxPerformance);
  const startManagement = feeToPoints(fund.pending_management_fee ?? fund.management_fee);
  const startPerformance = feeToPoints(fund.pending_performance_fee ?? fund.performance_fee);
  const [management, setManagement] = useState(() => snapFee(startManagement, capManagement));
  const [performance, setPerformance] = useState(() => snapFee(startPerformance, capPerformance));
  const setFees = useSetFundFees(fund.id);
  const propose = useProposeFeeIncrease(fund.id);

  const changed =
    feeToBody(management) !== feeToBody(startManagement) || feeToBody(performance) !== feeToBody(startPerformance);

  // Subir acima das taxas em vigor é votação dos cotistas; baixar ou manter é decisão do gestor
  const raises =
    fundStage(fund) === "listed" &&
    raisesFee({ management: fund.management_fee, performance: fund.performance_fee }, { management, performance });
  const reason = raises ? blockReason(optionOf(fund.assembly, "FEE_INCREASE"), fund.assembly) : null;
  const mutation = raises ? propose : setFees;

  const submit = () =>
    mutation.mutate(
      { management_fee: feeToBody(management), performance_fee: feeToBody(performance) },
      { onSuccess: () => onOpenChange(false) },
    );

  return (
    <>
      <DialogBody>
        <FeeControls
          managementPoints={management}
          onManagementChange={setManagement}
          performancePoints={performance}
          onPerformanceChange={setPerformance}
          maxManagement={rules.maxManagement}
          maxPerformance={rules.maxPerformance}
          netWorth={netWorthOf(fund)}
          waterMark={<WaterMarkToday fund={fund} />}
        />
        {raises ? (
          <RaiseNote fund={fund} management={management} performance={performance} />
        ) : (
          <Alert variant="info">
            <CalendarClock />
            <AlertTitle>A taxa nova vale no mês seguinte</AlertTitle>
            <AlertDescription>
              A mudança entra no primeiro dia útil do mês que vem, e o jornal avisa a sala antes. Até lá valem as taxas
              de hoje.
            </AlertDescription>
          </Alert>
        )}
        {reason !== null && <p className="text-[13px] text-destructive">{reason}</p>}
      </DialogBody>
      <DialogFooter variant="divided">
        <Button variant="outline" onClick={() => onOpenChange(false)}>
          Cancelar
        </Button>
        <Button variant="fund" disabled={!changed || mutation.isPending || reason !== null} onClick={submit}>
          {mutation.isPending && <Spinner />}
          {raises ? "Levar à assembleia" : "Salvar as taxas"}
        </Button>
      </DialogFooter>
    </>
  );
}

/** Mudar as taxas do gestor, em réguas até o teto da partida; a mudança vale a partir do mês seguinte. */
export function FeesDialog({ open, onOpenChange, fund }: FeesDialogProps) {
  const { simulation } = useSimulation();
  const match = simulation?.simulation;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Taxas de {fund.name}</DialogTitle>
          <DialogDescription>
            O que você recebe dos cotistas pela gestão, dentro do teto que a sala escolheu.
          </DialogDescription>
        </DialogHeader>
        {match && (
          <FeesForm
            fund={fund}
            rules={{ maxManagement: match.fund_max_management_fee, maxPerformance: match.fund_max_performance_fee }}
            onOpenChange={onOpenChange}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
