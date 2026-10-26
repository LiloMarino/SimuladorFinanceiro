import { useState, type DragEvent } from "react";
import { FileText, TriangleAlert, Upload, X } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { displayDate, displayNumber } from "@/shared/lib/utils/display";
import { inspectCsv, type CsvInspection } from "../lib/csv-file";

type CsvDropzoneProps = {
  id: string;
  picked: CsvInspection | null;
  disabled?: boolean;
  onPick: (picked: CsvInspection | null) => void;
};

const formatKilobytes = (bytes: number) => `${Math.max(1, Math.round(bytes / 1024))} KB`;

/** Área para soltar ou escolher o CSV; mostra o arquivo escolhido ou o que está errado com ele. */
export function CsvDropzone({ id, picked, disabled, onPick }: CsvDropzoneProps) {
  const [dragging, setDragging] = useState(false);

  const pick = async (file: File | undefined) => {
    if (file) onPick(await inspectCsv(file));
  };
  const onDrop = (event: DragEvent<HTMLElement>) => {
    event.preventDefault();
    setDragging(false);
    if (!disabled) void pick(event.dataTransfer.files[0]);
  };

  // Arquivo escolhido e aceito
  if (picked && !picked.problem) {
    const period = picked.from && picked.to ? ` · ${displayDate(picked.from)} → ${displayDate(picked.to)}` : "";
    return (
      <div className="flex items-center gap-3 rounded-[10px] border border-input bg-subtle p-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-info-soft text-primary">
          <FileText className="size-4" />
        </span>
        <span className="grid min-w-0 flex-1">
          <span className="truncate font-mono text-[13px] font-medium">{picked.file.name}</span>
          <span className="text-xs text-muted-foreground">
            {formatKilobytes(picked.file.size)}
            {picked.rows !== null && ` · ${displayNumber(picked.rows, 0)} pregões`}
            {period}
          </span>
        </span>
        <Button
          variant="ghost"
          size="icon-xs"
          aria-label="Remover arquivo"
          disabled={disabled}
          onClick={() => onPick(null)}
        >
          <X />
        </Button>
      </div>
    );
  }

  // Arquivo que não serve
  if (picked?.problem) {
    return (
      <div
        role="alert"
        className="grid justify-items-center gap-1.5 rounded-[10px] border border-dashed border-destructive bg-destructive-soft p-4 text-center"
      >
        <TriangleAlert className="size-5 text-destructive" />
        <span className="text-[13px] font-semibold text-destructive">{picked.problem.title}</span>
        <span className="text-xs text-muted-foreground">{picked.problem.hint}</span>
        <Button variant="outline" size="sm" disabled={disabled} onClick={() => onPick(null)}>
          Escolher outro
        </Button>
      </div>
    );
  }

  return (
    // Soltar o arquivo é atalho do mouse; o teclado usa o input de arquivo que o label aciona.
    // oxlint-disable-next-line jsx-a11y/no-noninteractive-element-interactions
    <label
      htmlFor={id}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      className={cn(
        "flex h-28 cursor-pointer flex-col items-center justify-center gap-1 rounded-[10px] border border-dashed border-input text-center transition-colors hover:bg-subtle",
        dragging && "border-2 border-primary bg-info-soft hover:bg-info-soft",
        disabled && "pointer-events-none opacity-50",
      )}
    >
      <input
        id={id}
        type="file"
        accept=".csv"
        className="sr-only"
        disabled={disabled}
        onChange={(event) => {
          void pick(event.target.files?.[0]);
          event.target.value = "";
        }}
      />
      <Upload className="size-5 text-primary" />
      {dragging ? (
        <span className="text-[13px] font-semibold">Solte pra carregar</span>
      ) : (
        <>
          <span className="text-[13px] font-semibold">Arraste o CSV aqui</span>
          <span className="text-xs text-muted-foreground">
            ou <span className="font-medium text-primary">escolha no computador</span> · .csv até 5 MB
          </span>
        </>
      )}
    </label>
  );
}
