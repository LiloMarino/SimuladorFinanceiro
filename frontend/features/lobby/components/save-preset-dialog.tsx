import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Info } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import type { SavePresetRequest } from "@/types";
import { useSavePreset } from "../hooks/mutations/useSavePreset";
import { NAME_TAKEN_MESSAGE, NAME_TAKEN_STATUS, PRESET_NAME_MAX, presetIncludes } from "../lib/preset";
import type { SimulationFormValues } from "./lobby-match";

const nameSchema = z.object({
  name: z.string().trim().min(1, "Dê um nome para o preset").max(PRESET_NAME_MAX, `Até ${PRESET_NAME_MAX} letras`),
});

type SavePresetDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** As regras de agora: o que o preset guarda */
  values: SimulationFormValues;
  rules: SavePresetRequest["rules"];
};

/** Salvar as regras de agora com um nome: o diálogo mostra o que entra antes de pedir o nome. */
export function SavePresetDialog({ open, onOpenChange, values, rules }: SavePresetDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-105">
        <SavePresetForm values={values} rules={rules} onClose={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}

type SavePresetFormProps = Pick<SavePresetDialogProps, "values" | "rules"> & { onClose: () => void };

function SavePresetForm({ values, rules, onClose }: SavePresetFormProps) {
  const form = useForm<z.infer<typeof nameSchema>>({
    resolver: zodResolver(nameSchema),
    mode: "onChange",
    defaultValues: { name: "" },
  });
  const { mutate: save, isPending: saving } = useSavePreset();
  const canSave = form.formState.isValid && !form.formState.errors.name && !saving;

  const submit = form.handleSubmit(({ name }) => {
    save(
      { name, rules },
      {
        onSuccess: (preset) => {
          toast.success(
            <span>
              Preset salvo. <b>{preset.name}</b>
            </span>,
          );
          onClose();
        },
        onError: (err) => {
          if (err.status === NAME_TAKEN_STATUS) form.setError("name", { type: "server", message: NAME_TAKEN_MESSAGE });
        },
      },
    );
  });

  return (
    <form onSubmit={(event) => void submit(event)} className="grid gap-4">
      <DialogHeader>
        <DialogTitle>Salvar como preset</DialogTitle>
        <DialogDescription>Guarda as regras de agora para carregar com um clique.</DialogDescription>
      </DialogHeader>

      <Controller
        control={form.control}
        name="name"
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid}>
            <FieldLabel htmlFor="preset-name">Nome do preset</FieldLabel>
            <Input
              {...field}
              id="preset-name"
              autoFocus
              placeholder="Ex.: Sexta com a turma"
              aria-invalid={fieldState.invalid}
            />
            <FieldDescription>Até {PRESET_NAME_MAX} letras. Só você, o host, vê os seus presets.</FieldDescription>
            <FieldError errors={[fieldState.error]} />
          </Field>
        )}
      />

      {/* O que entra */}
      <div>
        <div className="mb-1 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
          O que entra
        </div>
        <dl>
          {presetIncludes(values).map((row) => (
            <div
              key={row.label}
              className="flex items-center justify-between gap-3 border-t py-1.75 text-[13px] first:border-t-0"
            >
              <dt className="shrink-0 text-muted-foreground">{row.label}</dt>
              <dd className="min-w-0 truncate text-right">{row.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      <div className="flex gap-2 rounded-[10px] bg-subtle px-3 py-2.5 text-xs text-muted-foreground">
        <Info className="mt-px size-3.5 shrink-0" />
        <span>
          Não entram o nome da partida, gerado a cada uma, nem quem está em cada equipe. O futuro gerado continua na
          Central de dados e vale para todas as partidas.
        </span>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button type="submit" disabled={!canSave}>
          {saving && <Spinner />}
          Salvar preset
        </Button>
      </DialogFooter>
    </form>
  );
}
