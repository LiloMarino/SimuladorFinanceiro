import type { ReactNode } from "react";
import { CircleAlert, Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";

type PreparationFooterProps = {
  /** O que fica no perfil e o que vale só nesta sala */
  note: ReactNode;
  /** A recusa do último Salvar; o botão vira "Tentar de novo" */
  error?: string | null;
  saving?: boolean;
  /** Sem Salvar quando a aba não tem o que gravar */
  canSave?: boolean;
  onClose: () => void;
};

/** Rodapé de cada aba: o resumo do que se grava, Fechar e Salvar, e a recusa do servidor acima deles. */
export function PreparationFooter({ note, error, saving = false, canSave, onClose }: PreparationFooterProps) {
  return (
    <div className="grid gap-3 rounded-b-xl border-t bg-subtle px-6 py-3.5">
      {error && (
        <Alert variant="destructive">
          <CircleAlert />
          <AlertTitle>Não deu para salvar a preparação</AlertTitle>
          <AlertDescription>{error} Nada se perdeu: os campos continuam como você deixou.</AlertDescription>
        </Alert>
      )}
      <div className="flex items-center gap-2">
        <span className="inline-flex flex-1 items-center gap-1.5 text-[12.5px] text-muted-foreground">
          <Info className="size-3.5 shrink-0 text-faint-foreground" />
          {note}
        </span>
        <Button type="button" variant="outline" onClick={onClose}>
          Fechar
        </Button>
        {canSave !== undefined && (
          <Button type="submit" disabled={!canSave || saving}>
            {saving && <Spinner />}
            {error ? "Tentar de novo" : "Salvar"}
          </Button>
        )}
      </div>
    </div>
  );
}
