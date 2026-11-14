import { FundMark } from "@/shared/components/fund-mark";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";

/** Aviso das boletas com uma gestora ativa: de qual caixa a ordem sai e como voltar para a pessoal. Sem gestora ativa não aparece. */
export function AccountOriginNotice() {
  const { fund } = useActiveAccount();
  if (!fund) return null;

  return (
    <div className="flex items-center gap-2.5 rounded-[10px] bg-fund-soft px-3 py-2.5 text-[13px]">
      <FundMark name={fund.name} />
      <span>
        Ordem pela <b className="font-bold">{fund.name}</b>. Para usar a sua carteira, troque no caixa, lá em cima.
      </span>
    </div>
  );
}
