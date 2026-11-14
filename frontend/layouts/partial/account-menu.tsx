import { Check } from "lucide-react";
import { FundMark } from "@/shared/components/fund-mark";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import {
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/shared/components/ui/dropdown-menu";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayIsoDate, displayMoney } from "@/shared/lib/utils/display";
import type { FundAccount } from "@/types";
import { FrozenLock } from "./frozen-lock";

type AccountMenuProps = {
  accounts: FundAccount[];
  active: FundAccount;
  onSelect: (fundId: number | null) => void;
};

/** Menu "Operar com": cada conta com o próprio caixa e a escolhida marcada. */
export function AccountMenu({ accounts, active, onSelect }: AccountMenuProps) {
  const { user } = useAuth();
  const frozenUntil = accounts.every((account) => account.frozen_until !== null) ? accounts[0]?.frozen_until : null;

  return (
    <DropdownMenuContent align="end" className="w-85">
      <DropdownMenuLabel>Operar com</DropdownMenuLabel>

      {/* Contas */}
      {accounts.map((account) => {
        const isFund = account.fund_id !== null;
        const selected = account.fund_id === active.fund_id;

        return (
          <DropdownMenuItem
            key={account.fund_id ?? "personal"}
            size="rich"
            variant={selected ? (isFund ? "fund" : "selected") : "default"}
            className="items-center"
            onClick={() => onSelect(account.fund_id)}
          >
            {isFund ? (
              <FundMark name={account.name} />
            ) : (
              <PlayerAvatar nickname={user?.nickname ?? account.name} size="sm" />
            )}
            <span className="grid min-w-0">
              <b className="truncate font-semibold">{isFund ? account.name : "Carteira pessoal"}</b>
              <span className="font-mono text-xs text-muted-foreground">
                {account.ticker ? `${account.ticker} · ` : ""}caixa {displayMoney(account.cash)}
              </span>
            </span>
            <span className="ml-auto flex items-center gap-1.5">
              {account.frozen_until && <FrozenLock until={account.frozen_until} severalAccounts />}
              {selected && <Check className="size-3.5" />}
            </span>
          </DropdownMenuItem>
        );
      })}

      {/* Rodapé */}
      <DropdownMenuSeparator />
      <p className="px-2.5 py-1.5 text-xs text-muted-foreground">
        {frozenUntil
          ? `As contas estão congeladas até ${displayIsoDate(frozenUntil)}: dá para olhar, não para operar.`
          : "A conta escolhida vale para renda variável, renda fixa e Tesouro, até você trocar de novo."}
      </p>
    </DropdownMenuContent>
  );
}
