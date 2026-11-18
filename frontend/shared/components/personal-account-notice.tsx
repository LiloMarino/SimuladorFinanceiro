import { Wallet } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";

/** Aviso de quem opera pela carteira de uma gestora: levar da carteira e negociar cotas saem da carteira pessoal. */
export function PersonalAccountNotice({ children }: { children: string }) {
  const { switchAccount } = useActiveAccount();

  return (
    <Alert variant="warning">
      <Wallet />
      <AlertTitle>Você está na carteira de uma gestora</AlertTitle>
      <AlertDescription>{children}</AlertDescription>
      <AlertAction>
        <Button size="sm" variant="outline" onClick={() => switchAccount(null)}>
          Usar minha carteira
        </Button>
      </AlertAction>
    </Alert>
  );
}
