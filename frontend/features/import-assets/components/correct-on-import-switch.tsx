import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { useSaveImportSettings } from "../hooks/mutations/useSaveImportSettings";
import { useImportSettings } from "../hooks/queries/useImportSettings";

/** Chave que decide se a importação troca por interpolação os dias em que a fonte errou o preço. */
export function CorrectOnImportSwitch() {
  const { data: settings } = useImportSettings();
  const save = useSaveImportSettings();

  return (
    <div className="flex h-8 items-center gap-2 rounded-lg border border-input px-3">
      <Switch
        id="correct-on-import"
        checked={settings?.correct_price_errors ?? true}
        disabled={!settings || save.isPending}
        onCheckedChange={(checked) => save.mutate({ correct_price_errors: checked })}
      />
      <Tooltip>
        <TooltipTrigger render={<Label htmlFor="correct-on-import" />}>Corrigir ao importar</TooltipTrigger>
        <TooltipContent side="top" className="max-w-64">
          Ligada, a importação troca por interpolação os dias em que o yfinance errou o preço (queda de 99% que volta em
          poucos pregões). Desligada, o dado entra como a fonte mandou, com os erros. Vale para as próximas importações;
          o que já está na base só muda pelo botão ao lado. Cripto nunca é corrigida.
        </TooltipContent>
      </Tooltip>
    </div>
  );
}
