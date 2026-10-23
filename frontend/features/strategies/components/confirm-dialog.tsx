import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { Spinner } from "@/shared/components/ui/spinner";
import { KeyValueRow } from "@/shared/components/key-value-row";
import type { StrategyInfo } from "@/types";
import type { ParamValues } from "../lib/strategy-params";

/** A mudança de modo que espera a confirmação do jogador. */
export type ModeChange =
  | { kind: "turn-on"; key: string; params: ParamValues }
  | { kind: "switch"; key: string; params: ParamValues }
  | { kind: "manual" };

type ConfirmDialogProps = {
  change: ModeChange | null;
  strategies: StrategyInfo[];
  /** A estratégia ligada agora, se houver */
  activeKey: string | undefined;
  /** Ordens abertas do jogador, canceladas por qualquer mudança de modo */
  openOrders: number;
  pending: boolean;
  onCancel: () => void;
  onConfirm: (change: ModeChange) => void;
};

/** Confirma ligar, trocar ou desligar: avisa das ordens abertas que serão canceladas. */
export function ConfirmDialog({
  change,
  strategies,
  activeKey,
  openOrders,
  pending,
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  const nameOf = (key: string | undefined) =>
    strategies.find((strategy) => strategy.key === key)?.name ?? "A estratégia";
  const cancels = openOrders > 0 ? ` e cancelar ${openOrders} ${openOrders === 1 ? "ordem" : "ordens"}` : "";

  const copy = !change
    ? null
    : change.kind === "turn-on"
      ? {
          title: "Ligar o automático?",
          description: `${nameOf(change.key)} passa a operar por você a partir do próximo dia da partida.`,
          tickets: "travadas enquanto estiver ligado",
          action: `Ligar${cancels}`,
        }
      : change.kind === "switch"
        ? {
            title: "Trocar de estratégia?",
            description: `${nameOf(activeKey)} deixa de operar e ${nameOf(change.key)} assume a partir do próximo dia da partida.`,
            tickets: "continuam travadas",
            action: `Trocar${cancels}`,
          }
        : {
            title: "Voltar ao manual?",
            description: `${nameOf(activeKey)} deixa de operar. O que ela já comprou continua na sua carteira.`,
            tickets: "liberadas para operar à mão",
            action: openOrders > 0 ? `Voltar${cancels}` : "Voltar ao manual",
          };

  return (
    <AlertDialog open={change !== null} onOpenChange={(open) => !open && !pending && onCancel()}>
      <AlertDialogContent>
        {copy && change && (
          <>
            <AlertDialogHeader>
              <AlertDialogTitle>{copy.title}</AlertDialogTitle>
              <AlertDialogDescription>{copy.description}</AlertDialogDescription>
            </AlertDialogHeader>

            <div>
              <KeyValueRow
                label="Suas ordens abertas"
                value={
                  openOrders > 0
                    ? `${openOrders} ${openOrders === 1 ? "será cancelada" : "serão canceladas"}`
                    : "nenhuma"
                }
                valueClassName={openOrders > 0 ? "font-sans font-medium text-warning" : "font-sans font-medium"}
              />
              <KeyValueRow label="Boletas" value={copy.tickets} valueClassName="font-sans font-medium" />
            </div>

            <AlertDialogFooter>
              <AlertDialogCancel size="sm" disabled={pending}>
                Cancelar
              </AlertDialogCancel>
              <AlertDialogAction size="sm" disabled={pending} onClick={() => onConfirm(change)}>
                {pending && <Spinner />}
                {copy.action}
              </AlertDialogAction>
            </AlertDialogFooter>
          </>
        )}
      </AlertDialogContent>
    </AlertDialog>
  );
}
