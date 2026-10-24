import { Field, FieldContent, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Switch } from "@/shared/components/ui/switch";
import { useSaveImportSettings } from "../hooks/mutations/useSaveImportSettings";
import { useImportSettings } from "../hooks/queries/useImportSettings";

/** Chave que decide se a importação troca por interpolação os dias em que a fonte errou o preço. */
export function CorrectOnImportSwitch() {
  const { data: settings } = useImportSettings();
  const save = useSaveImportSettings();

  return (
    <Field orientation="horizontal">
      <Switch
        id="correct-on-import"
        checked={settings?.correct_price_errors ?? true}
        disabled={!settings || save.isPending}
        onCheckedChange={(checked) => save.mutate({ correct_price_errors: checked })}
      />
      <FieldContent>
        <FieldLabel htmlFor="correct-on-import">Corrigir erros de dado ao importar</FieldLabel>
        <FieldDescription>
          Troca por interpolação o dia em que o yFinance errou o preço (queda de 99% que volta em poucos pregões).
          Desligado, o dado entra como a fonte mandou. Cripto nunca é corrigida.
        </FieldDescription>
      </FieldContent>
    </Field>
  );
}
