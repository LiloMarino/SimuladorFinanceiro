import { Newspaper } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

/** Aviso da página de um ativo enquanto o presidente opera pelo Fundo Soberano: o destino de cada ordem. */
export function SovereignAccountNotice() {
  return (
    <Alert variant="warning">
      <Newspaper />
      <AlertDescription>
        <b className="font-semibold">Toda compra e venda do Fundo Soberano sai no jornal</b>, com o nome do presidente.
        O dinheiro de uma venda volta ao Tesouro.
      </AlertDescription>
    </Alert>
  );
}
