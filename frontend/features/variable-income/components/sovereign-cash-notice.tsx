import { Landmark } from "lucide-react";
import { Link } from "react-router-dom";
import { displayMoney } from "@/shared/lib/utils/display";
import type { FundAccount } from "@/types";

/** O caixa do Fundo Soberano na boleta: só o aporte aprovado o enche, então sem caixa o caminho do aporte aparece aqui. */
export function SovereignCashNotice({ account }: { account: FundAccount }) {
  const noCash = Number(account.cash) === 0;

  return (
    <div className="flex items-center gap-2.5 rounded-lg border border-border bg-subtle px-3 py-2.5 text-[13px]">
      <Landmark className="size-4 shrink-0 text-muted-foreground" />
      <span className="grid gap-0.5">
        <b className="font-semibold">
          Caixa do {account.name}: {displayMoney(account.cash)}
        </b>
        {noCash && (
          <span className="text-xs text-muted-foreground">
            A compra sai desse caixa, que só enche com um aporte aprovado no Congresso.
          </span>
        )}
      </span>
      {noCash && (
        <Link
          to="/government?tab=state-companies"
          className="ml-auto text-xs font-medium whitespace-nowrap text-primary hover:text-primary-hover"
        >
          Propor aporte
        </Link>
      )}
    </div>
  );
}
