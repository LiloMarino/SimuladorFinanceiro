import { Button } from "@/shared/components/ui/button";
import { FundMark } from "@/shared/components/fund-mark";
import { cn } from "@/shared/lib/utils";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { accountTone } from "@/shared/lib/active-account";

const BANNER_COLORS = {
  fund: "border-fund bg-fund text-fund-foreground",
  government: "border-expansion-government bg-expansion-government text-expansion-government-foreground",
} as const;

/** Faixa sob a topbar enquanto o jogador opera pela conta de uma gestora ou pelo Fundo Soberano. */
export function FundBanner() {
  const { active, switchAccount } = useActiveAccount();
  const tone = accountTone(active);
  if (!active || tone === "personal") return null;
  const sovereign = tone === "government";

  return (
    <div className={cn("flex items-center gap-2.5 border-t px-7 py-2 text-[13px]", BANNER_COLORS[tone])}>
      <FundMark name={active.name} tone="inverse" palette={tone} />
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
      <Button
        variant={sovereign ? "link-government" : "link-fund"}
        size="sm"
        className="ml-auto"
        onClick={() => switchAccount(null)}
      >
        {sovereign ? "Voltar para o seu caixa" : "Voltar para a carteira pessoal"}
      </Button>
    </div>
  );
}
