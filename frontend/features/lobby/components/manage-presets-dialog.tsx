import { useState } from "react";
import { Check, Info, Pencil, Trash2, X } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { FieldError } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { Preset } from "@/types";
import { useDeletePreset } from "../hooks/mutations/useDeletePreset";
import { useRenamePreset } from "../hooks/mutations/useRenamePreset";
import { NAME_TAKEN_MESSAGE, NAME_TAKEN_STATUS, PRESET_NAME_MAX } from "../lib/preset";

type ManagePresetsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Os presets do host: os prontos não se renomeiam nem se apagam */
  presets: Preset[];
};

/** Renomear e apagar os presets do host, fora da lista de escolha. */
export function ManagePresetsDialog({ open, onOpenChange, presets }: ManagePresetsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-105">
        <DialogHeader>
          <DialogTitle>Meus presets</DialogTitle>
          <DialogDescription>Renomeie ou apague. Apagar não muda nenhuma partida já criada.</DialogDescription>
        </DialogHeader>

        {/* Listagem dos presets do host */}
        <div>
          {presets.map((preset) => (
            <ManagePresetRow key={preset.id} preset={preset} />
          ))}
        </div>

        <div className="flex gap-2 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" />
          <span>Iniciante, Clássico e Realista vêm com o app e não se renomeiam nem se apagam.</span>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

type Mode = "view" | "rename" | "delete";

function ManagePresetRow({ preset }: { preset: Preset }) {
  const [mode, setMode] = useState<Mode>("view");
  const [name, setName] = useState(preset.name);
  const [taken, setTaken] = useState(false);
  const { mutate: rename, isPending: renaming } = useRenamePreset();
  const { mutate: remove, isPending: removing } = useDeletePreset();

  const trimmed = name.trim();
  const canRename = trimmed.length > 0 && !taken && !renaming;

  const submitRename = () => {
    if (!canRename) return;
    rename(
      { presetId: preset.id, name: trimmed },
      {
        onSuccess: () => setMode("view"),
        onError: (err) => setTaken(err.status === NAME_TAKEN_STATUS),
      },
    );
  };

  if (mode === "delete") {
    return (
      <div className="-mx-2.5 flex items-center gap-2.5 rounded-lg bg-destructive-soft px-2.5 py-2.5 text-[13px]">
        <span className="flex-1">
          Apagar <b>{preset.name}</b>? Não dá para desfazer.
        </span>
        <Button size="sm" variant="outline" onClick={() => setMode("view")}>
          Cancelar
        </Button>
        <Button size="sm" variant="destructive" disabled={removing} onClick={() => remove(preset.id)}>
          Apagar
        </Button>
      </div>
    );
  }

  if (mode === "rename") {
    return (
      <div className="border-t py-2.5 first:border-t-0">
        <div className="flex items-center gap-2.5">
          <Input
            value={name}
            maxLength={PRESET_NAME_MAX}
            autoFocus
            aria-label={`Novo nome de ${preset.name}`}
            aria-invalid={taken}
            onChange={(event) => {
              setName(event.target.value);
              setTaken(false);
            }}
            onKeyDown={(event) => event.key === "Enter" && submitRename()}
          />
          <Button size="icon-sm" variant="ghost" aria-label="Salvar nome" disabled={!canRename} onClick={submitRename}>
            <Check className="text-success" />
          </Button>
          <Button
            size="icon-sm"
            variant="ghost"
            aria-label="Cancelar"
            onClick={() => {
              setName(preset.name);
              setTaken(false);
              setMode("view");
            }}
          >
            <X />
          </Button>
        </div>
        {taken && <FieldError errors={[{ message: NAME_TAKEN_MESSAGE }]} className="mt-1.5" />}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2.5 border-t py-2.5 first:border-t-0">
      <span className="grid min-w-0 flex-1">
        <b className="truncate text-[13px] font-semibold">{preset.name}</b>
        <span className="text-xs text-muted-foreground">salvo em {displayIsoDate(preset.created_at.slice(0, 10))}</span>
      </span>
      <Button size="icon-sm" variant="ghost" aria-label={`Renomear ${preset.name}`} onClick={() => setMode("rename")}>
        <Pencil />
      </Button>
      <Button size="icon-sm" variant="ghost" aria-label={`Apagar ${preset.name}`} onClick={() => setMode("delete")}>
        <Trash2 />
      </Button>
    </div>
  );
}
