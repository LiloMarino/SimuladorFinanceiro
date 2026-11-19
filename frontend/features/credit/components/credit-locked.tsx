import { Lock } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import type { CreditLock } from "../lib/credit-lock";

const TITLES: Record<CreditLock, string> = {
  sovereign: "Você está controlando o Fundo Soberano",
  comanager: "Você é co-gestor desta gestora",
};

const DESCRIPTIONS: Record<CreditLock, string> = {
  sovereign: "O Fundo Soberano não toma crédito. O empréstimo é da conta pessoal ou de uma gestora que você gere.",
  comanager: "O crédito em nome dela é do gestor principal; o seu crédito fica na conta pessoal.",
};

/** Tela travada do crédito: diz por que a conta ativa não pede empréstimo e oferece as contas que pedem. */
export function CreditLocked({ lock }: { lock: CreditLock }) {
  const { accounts, switchAccount } = useActiveAccount();
  const managed = (accounts ?? []).filter((account) => account.role === "manager");

  return (
    <Card>
      <CardContent>
        <Empty variant="dashed">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <Lock />
            </EmptyMedia>
            <EmptyTitle>{TITLES[lock]}</EmptyTitle>
            <EmptyDescription>{DESCRIPTIONS[lock]}</EmptyDescription>
          </EmptyHeader>
          <EmptyContent>
            <div className="flex flex-wrap justify-center gap-2">
              <Button onClick={() => switchAccount(null)}>Usar a conta pessoal</Button>
              {managed.map((account) => (
                <Button key={account.fund_id} variant="outline" onClick={() => switchAccount(account.fund_id)}>
                  {account.name}
                </Button>
              ))}
            </div>
          </EmptyContent>
        </Empty>
      </CardContent>
    </Card>
  );
}
