import { FundMark } from "@/shared/components/fund-mark";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { isSovereignAccount } from "@/shared/lib/active-account";

/** Aviso das boletas com uma gestora ou o Fundo Soberano ativo: de qual caixa a ordem sai e como voltar para a pessoal. Na conta pessoal não aparece. */
export function AccountOriginNotice() {
  const { fund } = useActiveAccount();
  if (!fund) return null;

  const sovereign = isSovereignAccount(fund);

  return (
    <div className="flex items-center gap-2.5 rounded-[10px] bg-fund-soft px-3 py-2.5 text-[13px]">
      <FundMark name={fund.name} />
      <span>
        Ordem {sovereign ? "pelo" : "pela"} <b className="font-bold">{fund.name}</b>
        {sovereign ? ", com o caixa dos aportes aprovados" : ""}. Para usar a sua carteira, troque no caixa, lá em cima.
      </span>
    </div>
  );
}
