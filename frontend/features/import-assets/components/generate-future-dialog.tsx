import { useState } from "react";
import { Dialog, DialogContent } from "@/shared/components/ui/dialog";
import { useSeriesCoverage } from "@/shared/hooks/queries/useSeriesCoverage";
import { useGeneratedFuture } from "../hooks/queries/useGeneratedFuture";
import { FutureForm } from "./future-form";

type GenerateFutureDialogProps = {
  open: boolean;
  /** Abre com uma semente nova em vez da gravada */
  redrawSeed: boolean;
  onOpenChange: (open: boolean) => void;
};

/** "Gerar dados futuros": o formulário só monta com o futuro gravado e a cobertura já resolvidos. */
export function GenerateFutureDialog({ open, redrawSeed, onOpenChange }: GenerateFutureDialogProps) {
  const { data: future } = useGeneratedFuture();
  const { data: coverage } = useSeriesCoverage();
  // Enquanto grava, o diálogo só fecha pela própria gravação
  const [recording, setRecording] = useState(false);

  if (future === undefined || coverage === undefined) return null;

  return (
    <Dialog open={open} onOpenChange={(next) => !recording && onOpenChange(next)}>
      <DialogContent showCloseButton={!recording} className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-290">
        <FutureForm
          future={future}
          coverage={coverage}
          redrawSeed={redrawSeed}
          onClose={() => onOpenChange(false)}
          onRecordingChange={setRecording}
        />
      </DialogContent>
    </Dialog>
  );
}
