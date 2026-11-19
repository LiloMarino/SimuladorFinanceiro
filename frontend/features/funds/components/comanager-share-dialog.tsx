import { useState } from "react";
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
import type { FundDetails } from "@/types";
import { useUpdateComanagerShare } from "../hooks/mutations/useUpdateComanagerShare";
import { maxSharePoints } from "@/shared/lib/fund-comanager-shares";
import { futureShareOf, othersPoints, type Comanager } from "../lib/fund-comanagers";
import { feeToBody } from "../lib/fund-fees";
import { ComanagerShareControls } from "./comanager-share-controls";

type ComanagerShareDialogProps = {
  /** O co-gestor que muda de parte; nulo com o diálogo fechado */
  comanager: Comanager | null;
  onClose: () => void;
  fund: FundDetails;
};

type ShareFormProps = { comanager: Comanager; fund: FundDetails; onClose: () => void };

/** O formulário parte da parte que vai valer: a agendada, se houver, senão a de hoje. */
function ShareForm({ comanager, fund, onClose }: ShareFormProps) {
  const update = useUpdateComanagerShare(fund.id);
  const others = othersPoints(fund.comanagers, comanager.user_id);
  const max = maxSharePoints(others);
  const start = Math.round(futureShareOf(comanager) * 100);
  const [points, setPoints] = useState(Math.min(start, max));

  const submit = () => update.mutate({ userId: comanager.user_id, share: feeToBody(points) }, { onSuccess: onClose });

  return (
    <>
      <DialogBody>
        <ComanagerShareControls
          points={points}
          onChange={setPoints}
          others={others}
          max={max}
          nickname={comanager.nickname}
          monthly={Number(fund.fees.management_monthly_estimate)}
        />
      </DialogBody>
      <DialogFooter variant="divided">
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button variant="fund" disabled={points === start || update.isPending} onClick={submit}>
          {update.isPending && <Spinner />}
          Salvar a parte
        </Button>
      </DialogFooter>
    </>
  );
}

/** Mudar a parte de um co-gestor nas taxas; a nova parte vale no mês seguinte. */
export function ComanagerShareDialog({ comanager, onClose, fund }: ComanagerShareDialogProps) {
  return (
    <Dialog open={comanager !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Parte de {comanager?.nickname}</DialogTitle>
          <DialogDescription>Quanto das taxas de {fund.name} vai para este co-gestor.</DialogDescription>
        </DialogHeader>
        {comanager && <ShareForm comanager={comanager} fund={fund} onClose={onClose} />}
      </DialogContent>
    </Dialog>
  );
}
