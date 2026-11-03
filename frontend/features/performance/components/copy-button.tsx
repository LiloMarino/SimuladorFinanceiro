import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

/** Copia um comando de terminal para a área de transferência. */
export function CopyButton({ text, variant = "inverse" }: { text: string; variant?: "inverse" | "outline" }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Sem permissão para a área de transferência: o botão fica como estava
    }
  }

  return (
    <Button variant={variant} size="xs" onClick={() => void copy()}>
      {copied ? <Check /> : <Copy />}
      {copied ? "Copiado" : "Copiar"}
    </Button>
  );
}
