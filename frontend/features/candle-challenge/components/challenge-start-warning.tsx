import { TriangleAlert } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
interface ChallengeStartWarningProps {
  question: number;
  pending: boolean;
  disabled: boolean;
  onConfirm: () => void;
}

/** No lugar do botão de iniciar, para o host: iniciar a partida encerra o desafio que está rolando. */
export function ChallengeStartWarning({ question, pending, disabled, onConfirm }: ChallengeStartWarningProps) {
  return (
    <div className="grid grid-cols-[auto_1fr] items-center gap-x-3 gap-y-2.5 rounded-xl border border-warning/30 bg-warning-soft px-4 py-3.5">
      <TriangleAlert className="size-5 text-warning" />
      <div className="grid gap-0.5">
        <b>O desafio da vela está rolando</b>
        <span className="text-[13px]">Iniciar a partida encerra a pergunta {question} de 10, sem vencedor.</span>
      </div>
      <Button className="col-span-2" disabled={disabled} onClick={onConfirm}>
        {pending && <Spinner />}
        Iniciar mesmo assim
      </Button>
    </div>
  );
}
