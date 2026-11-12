import type { ReactNode } from "react";
import { Check, CircleAlert, Info } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";

type PreparationFooterProps = {
  /** O que fica no perfil e o que vale só nesta sala */
  note: ReactNode;
  /** O salvamento automático em curso; ausente quando a aba não grava nada */
  saving?: boolean | undefined;
  /** A recusa do último salvamento; "Tentar de novo" refaz o mesmo pedido */
  error?: string | null;
  /** O que falta preencher para o salvamento automático gravar */
  incomplete?: string | null;
  onRetry?: () => void;
  onClose: () => void;
};

/** Rodapé de cada aba: o resumo do que se grava, o estado do salvamento automático e Fechar. */
export function PreparationFooter({ note, saving, error, incomplete, onRetry, onClose }: PreparationFooterProps) {
  return (
    <div className="grid gap-3 rounded-b-xl border-t bg-subtle px-6 py-3.5">
      {error && (
        <Alert variant="destructive">
          <CircleAlert />
          <AlertTitle>Não deu para salvar a preparação</AlertTitle>
          <AlertDescription>{error} Nada se perdeu: os campos continuam como você deixou.</AlertDescription>
          {onRetry && (
            <AlertAction>
              <Button type="button" size="sm" variant="outline" onClick={onRetry}>
                Tentar de novo
              </Button>
            </AlertAction>
          )}
        </Alert>
      )}
      <div className="flex items-center gap-3">
        <span className="inline-flex flex-1 items-center gap-1.5 text-[12.5px] text-muted-foreground">
          <Info className="size-3.5 shrink-0 text-faint-foreground" />
          {note}
        </span>
        {saving !== undefined && <SaveStatus saving={saving} incomplete={incomplete ?? null} failed={!!error} />}
        <Button type="button" variant="outline" onClick={onClose}>
          Fechar
        </Button>
      </div>
    </div>
  );
}

function SaveStatus({ saving, incomplete, failed }: { saving: boolean; incomplete: string | null; failed: boolean }) {
  if (saving) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground" role="status">
        <Spinner className="size-3.5" /> Salvando…
      </span>
    );
  }
  if (failed) return null;
  if (incomplete) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-warning" role="status">
        <CircleAlert className="size-3.5" /> {incomplete}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium text-success" role="status">
      <Check className="size-3.5" /> Salvo automaticamente
    </span>
  );
}
