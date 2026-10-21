import { Sparkles } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useGeneratedFuture } from "../hooks/queries/useGeneratedFuture";

/** Abre o diálogo de geração: "Gerar dados futuros" na primeira vez, "Gerar outro futuro" depois. */
export function GenerateFutureButton({ onClick }: { onClick: () => void }) {
  const { data: future } = useGeneratedFuture();

  return (
    <Button variant="outline" disabled={future === undefined} onClick={onClick}>
      <Sparkles className="text-warning" />
      {future ? "Gerar outro futuro" : "Gerar dados futuros"}
    </Button>
  );
}
