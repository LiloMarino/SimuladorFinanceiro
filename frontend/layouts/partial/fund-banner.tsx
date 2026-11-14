import { Button } from "@/shared/components/ui/button";
import { FundMark } from "@/shared/components/fund-mark";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";

/** Faixa sob a topbar enquanto o jogador opera pela conta de uma gestora. */
export function FundBanner() {
  const { active, switchAccount } = useActiveAccount();
  if (!active || active.fund_id === null) return null;

  return (
    <div className="flex items-center gap-2.5 border-t border-fund bg-fund px-7 py-2 text-[13px] text-fund-foreground">
      <FundMark name={active.name} tone="inverse" />
      <span>
        Você está operando a <b className="font-semibold">{active.name}</b>: as ordens saem do caixa e da carteira dela,
        não dos seus.
      </span>
      <Button variant="link-fund" size="sm" className="ml-auto" onClick={() => switchAccount(null)}>
        Voltar para a carteira pessoal
      </Button>
    </div>
  );
}
