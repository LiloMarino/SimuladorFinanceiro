import { CircleCheck, TriangleAlert } from "lucide-react";
import { useNow } from "@/shared/hooks/useNow";

/** O que aconteceu com a última mudança das regras, como o hook de sincronização informa. */
export type RulesSaveStatus = {
  savedAt: number | null;
  saving: boolean;
  /** Restaurar os padrões em andamento: as regras estão sendo trocadas */
  restoring: boolean;
  saveError: Error | null;
  /** O servidor recusou a última escolha de assistências e o interruptor voltou ao valor salvo */
  rejectedAssistances: boolean;
  retryAssistances: () => void;
};

type SaveStatusProps = RulesSaveStatus & {
  isHost: boolean;
  locked: boolean;
  hostNickname: string;
  invalidFields: number;
};

/** Rodapé do painel: o que aconteceu com a última mudança, no lugar do toast repetido. */
export function SaveStatus({
  isHost,
  locked,
  hostNickname,
  invalidFields,
  savedAt,
  saving,
  saveError,
}: SaveStatusProps) {
  const now = useNow(1000);

  if (locked) {
    return <span className="text-[13px] text-muted-foreground">Regras de uma partida salva não mudam.</span>;
  }

  if (!isHost) {
    return (
      <span className="text-[13px] text-muted-foreground">
        Só {hostNickname} (host) edita. Você vê as mudanças na hora.
      </span>
    );
  }
  if (invalidFields > 0 || saveError) {
    return (
      <span className="flex items-center gap-1.5 text-[13px] text-destructive">
        <TriangleAlert className="size-3.5" />
        {invalidFields > 0
          ? `${invalidFields} ${invalidFields === 1 ? "campo com problema" : "campos com problema"}: nada foi salvo`
          : `Não salvou: ${saveError?.message}`}
      </span>
    );
  }
  if (saving) return <span className="text-[13px] text-muted-foreground">Salvando…</span>;
  if (savedAt) {
    const seconds = Math.max(0, Math.round((now - savedAt) / 1000));
    return (
      <span className="flex items-center gap-1.5 text-xs text-success">
        <CircleCheck className="size-3.5" />
        Salvo há {seconds} s · todos já veem
      </span>
    );
  }
  return <span className="text-[13px] text-muted-foreground">Mudanças salvam sozinhas.</span>;
}
