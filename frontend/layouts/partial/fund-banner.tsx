import { Button } from "@/shared/components/ui/button";
import { FundMark } from "@/shared/components/fund-mark";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { isSovereignAccount } from "@/shared/lib/active-account";

/** Faixa sob a topbar enquanto o jogador opera pela conta de uma gestora ou pelo Fundo Soberano. */
export function FundBanner() {
  const { active, switchAccount } = useActiveAccount();
  if (!active || active.fund_id === null) return null;
  const sovereign = isSovereignAccount(active);

  return (
    <div className="flex items-center gap-2.5 border-t border-fund bg-fund px-7 py-2 text-[13px] text-fund-foreground">
      <FundMark name={active.name} tone="inverse" />
      {sovereign ? (
        <span>
          Operando pelo <b className="font-semibold">{active.name}</b>. Toda compra e venda sai no jornal; venda volta
          ao Tesouro.
        </span>
      ) : (
        <span>
          Você está operando a <b className="font-semibold">{active.name}</b>: as ordens saem do caixa e da carteira
          dela, não dos seus.
        </span>
      )}
      <Button variant="link-fund" size="sm" className="ml-auto" onClick={() => switchAccount(null)}>
        {sovereign ? "Voltar para o seu caixa" : "Voltar para a carteira pessoal"}
      </Button>
    </div>
  );
}
