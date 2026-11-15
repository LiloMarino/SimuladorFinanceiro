import { useState } from "react";
import { OptionSelect } from "@/shared/components/option-select";
import { PlayerAvatar } from "@/shared/components/player-avatar";
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
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Spinner } from "@/shared/components/ui/spinner";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import type { FundDetails } from "@/types";
import { useInviteComanager } from "../hooks/mutations/useInviteComanager";
import { INVITE_DAYS, maxSharePoints, othersPoints } from "../lib/fund-comanagers";
import { feeToBody } from "../lib/fund-fees";
import { ComanagerShareControls } from "./comanager-share-controls";

type ComanagerInviteDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fund: FundDetails;
};

const DEFAULT_POINTS = 10;

type InviteFormProps = { fund: FundDetails; onOpenChange: (open: boolean) => void };

/** O formulário nasce a cada abertura: sem convidado escolhido e com a parte inicial dentro do que sobra. */
function InviteForm({ fund, onOpenChange }: InviteFormProps) {
  const { data: players } = useRoomPlayers();
  const invite = useInviteComanager(fund.id);
  const reserved = fund.comanagers.map((comanager) => comanager.nickname);
  const others = othersPoints(fund.comanagers, null);
  const max = maxSharePoints(others);
  const [nickname, setNickname] = useState<string | null>(null);
  const [points, setPoints] = useState(() => Math.min(DEFAULT_POINTS, max));

  const guests = (players ?? []).filter(
    (player) => player.bot === null && player.nickname !== fund.manager_nickname && !reserved.includes(player.nickname),
  );
  const options = guests.map((player) => ({
    value: player.nickname,
    label: player.nickname,
    description: `Tem ${INVITE_DAYS} dias para responder`,
    leading: <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />,
  }));

  const submit = () => {
    if (nickname === null) return;
    invite.mutate({ nickname, share: feeToBody(points) }, { onSuccess: () => onOpenChange(false) });
  };

  return (
    <>
      <DialogBody>
        <div className="grid gap-5">
          <Field>
            <FieldLabel htmlFor="comanager-guest">Quem convidar</FieldLabel>
            <OptionSelect
              id="comanager-guest"
              options={options}
              value={nickname}
              onChange={setNickname}
              placeholder="Escolha um jogador"
            />
            <FieldDescription>Só jogadores da sala: os bots não são convidados.</FieldDescription>
          </Field>
          <ComanagerShareControls
            points={points}
            onChange={setPoints}
            others={others}
            max={max}
            nickname={nickname ?? "O convidado"}
            monthly={Number(fund.fees.management_monthly_estimate)}
          />
        </div>
      </DialogBody>
      <DialogFooter variant="divided">
        <Button variant="outline" onClick={() => onOpenChange(false)}>
          Cancelar
        </Button>
        <Button variant="fund" disabled={nickname === null || invite.isPending} onClick={submit}>
          {invite.isPending && <Spinner />}
          Enviar o convite
        </Button>
      </DialogFooter>
    </>
  );
}

/** Convidar um co-gestor: o convite reserva a parte e vale por {INVITE_DAYS} dias. */
export function ComanagerInviteDialog({ open, onOpenChange, fund }: ComanagerInviteDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Convidar co-gestor de {fund.name}</DialogTitle>
          <DialogDescription>
            O co-gestor opera a carteira da gestora e divide com você as taxas. Quando ele aceita, o acesso abre na hora
            e a parte entra nas taxas do mês seguinte.
          </DialogDescription>
        </DialogHeader>
        {open && <InviteForm fund={fund} onOpenChange={onOpenChange} />}
      </DialogContent>
    </Dialog>
  );
}
