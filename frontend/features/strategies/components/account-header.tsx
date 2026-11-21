import { User } from "lucide-react";
import { FundMark } from "@/shared/components/fund-mark";
import type { FundAccount } from "@/types";

/** Diz de qual conta é o automático da página: a gestora que está no topo, ou a conta pessoal. */
export function AccountHeader({ fund }: { fund: FundAccount | null }) {
  return (
    <div className="flex items-center gap-2.5 text-[13px]">
      {fund ? <FundMark name={fund.name} size="md" /> : <User className="size-4 text-muted-foreground" />}
      {fund ? (
        <span>
          Automático da <b className="font-semibold">{fund.name}</b>
          <span className="text-muted-foreground"> · a estratégia opera a carteira dela, não a sua</span>
        </span>
      ) : (
        <span>
          Automático da <b className="font-semibold">sua conta pessoal</b>
        </span>
      )}
    </div>
  );
}
