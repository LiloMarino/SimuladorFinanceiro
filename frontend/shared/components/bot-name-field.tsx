import { Dices } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";

type BotNameFieldProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  /** Sorteia outro nome da lista da estratégia */
  onDraw: () => void;
  error?: { message?: string } | undefined;
  help?: string;
};

/** O nome do bot com o botão "Sortear". */
export function BotNameField({ id, value, onChange, onBlur, onDraw, error, help }: BotNameFieldProps) {
  return (
    <Field data-invalid={!!error}>
      <FieldLabel htmlFor={id}>Nome</FieldLabel>
      <div className="flex gap-2">
        <Input
          id={id}
          value={value}
          autoComplete="off"
          aria-invalid={!!error}
          onChange={(event) => onChange(event.target.value)}
          onBlur={onBlur}
        />
        <Button type="button" variant="outline" className="shrink-0" onClick={onDraw}>
          <Dices className="size-[15px]" />
          Sortear
        </Button>
      </div>
      {error ? <FieldError errors={[error]} /> : help && <FieldDescription>{help}</FieldDescription>}
    </Field>
  );
}
