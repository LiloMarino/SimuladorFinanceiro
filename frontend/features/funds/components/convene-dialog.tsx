import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
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
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Spinner } from "@/shared/components/ui/spinner";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useAuth } from "@/shared/hooks/useAuth";
import { useConveneAssembly } from "../hooks/mutations/useConveneAssembly";

const SELF = "self";

const conveneSchema = z.object({
  candidate: z.string().min(1, "Escolha quem assume a gestão"),
});

type ConveneValues = z.infer<typeof conveneSchema>;

type ConveneDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fundId: number;
  fundName: string;
  managerNickname: string | null;
};

/** Convocar a assembleia: indica a si mesmo ou um aliado jogador, que precisa aceitar antes de a votação abrir. */
export function ConveneDialog({ open, onOpenChange, fundId, fundName, managerNickname }: ConveneDialogProps) {
  const { user } = useAuth();
  const { data: players } = useRoomPlayers();
  const convene = useConveneAssembly(fundId);
  const form = useForm<ConveneValues>({
    resolver: zodResolver(conveneSchema),
    defaultValues: { candidate: SELF },
  });

  const allies = (players ?? []).filter(
    (player) => player.bot === null && player.nickname !== user?.nickname && player.nickname !== managerNickname,
  );
  const options = [
    { value: SELF, label: "Eu mesmo", description: "A votação abre agora" },
    ...allies.map((player) => ({
      value: player.nickname,
      label: player.nickname,
      description: "Precisa aceitar o convite em até 5 pregões",
      leading: <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />,
    })),
  ];

  const submit = form.handleSubmit(({ candidate }) =>
    convene.mutate(
      { candidate_nickname: candidate === SELF ? null : candidate },
      {
        onSuccess: () => {
          onOpenChange(false);
          form.reset();
        },
      },
    ),
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Convocar assembleia de {fundName}</DialogTitle>
          <DialogDescription>
            Os cotistas votam por 5 pregões, com o placar à vista. Vence quem tiver mais cotas entre os votantes, e o
            gestor conta contra, sozinho, com as cotas dele. Empate mantém o gestor.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <form id="convene-form" onSubmit={(event) => void submit(event)} className="grid gap-4">
            <Controller
              control={form.control}
              name="candidate"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="convene-candidate">Quem assume a gestão</FieldLabel>
                  <OptionSelect
                    id="convene-candidate"
                    options={options}
                    value={field.value}
                    onChange={field.onChange}
                    invalid={fieldState.invalid}
                  />
                  {fieldState.error ? (
                    <FieldError>{fieldState.error.message}</FieldError>
                  ) : (
                    <FieldDescription>
                      Quem convoca já entra com o voto a favor. Se a troca acontecer, o gestor atual fica só como
                      cotista e não pode fundar outra gestora por 6 meses.
                    </FieldDescription>
                  )}
                </Field>
              )}
            />
            <p className="rounded-lg bg-subtle px-3 py-2.5 text-xs text-muted-foreground">
              Enquanto a assembleia durar, a gestora não emite cotas. A recompra segue liberada e é a defesa do gestor:
              as cotas recompradas saem do total e do placar.
            </p>
          </form>
        </DialogBody>
        <DialogFooter variant="divided">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" form="convene-form" variant="fund" disabled={convene.isPending}>
            {convene.isPending && <Spinner />}
            Convocar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
