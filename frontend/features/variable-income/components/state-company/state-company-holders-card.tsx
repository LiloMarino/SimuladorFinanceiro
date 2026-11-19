import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { StackedBar } from "@/shared/components/stacked-bar";
import { displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { StateCompanyHolders } from "@/types";
import { holderShares } from "../../lib/state-company";

type HolderLine = {
  key: string;
  label: string;
  note?: string;
  share: number;
  /** A classe de cor do trecho dessa fatia na barra */
  color: string;
};

/** As fatias da empresa, na ordem da barra: governo, formador de mercado, jogadores, gestoras e bots. */
function holderLines(holders: StateCompanyHolders): HolderLine[] {
  const shares = holderShares(holders);
  const you = Number(holders.you);
  const lines: HolderLine[] = [
    {
      key: "government",
      label: "Governo",
      note: `${displayQuantity(holders.government)} ações · vende só pelo Fundo Soberano`,
      share: shares.government,
      color: "bg-expansion-government",
    },
    {
      key: "maker",
      label: "Formador de mercado",
      note: "compra e vende sempre, para a ação ter preço",
      share: shares.maker,
      color: "bg-chart-9",
    },
    {
      key: "players",
      label: "Jogadores",
      ...(you > 0 && { note: `você tem ${displayQuantity(holders.you)} ações, ${displayPercent(shares.you, 1)}` }),
      share: shares.players,
      color: "bg-chart-1",
    },
    { key: "funds", label: "Gestoras", share: shares.funds, color: "bg-chart-4" },
    { key: "bots", label: "Bots", share: shares.bots, color: "bg-risk-base" },
  ];
  return lines.filter((line) => line.key !== "funds" || line.share > 0);
}

/** A divisão das ações da estatal entre quem as tem, numa barra e em linhas. */
export function StateCompanyHoldersCard({ holders }: { holders: StateCompanyHolders }) {
  const lines = holderLines(holders);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quem tem as ações</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2.5">
          {/* Barra */}
          <StackedBar segments={lines.map((line) => ({ key: line.key, fraction: line.share, color: line.color }))} />

          {/* Linhas */}
          <div>
            {lines.map((line) => (
              <div
                key={line.key}
                className="flex items-baseline justify-between gap-4 border-t border-muted py-2.5 text-sm first:border-t-0"
              >
                <span className="grid">
                  {line.label}
                  {line.note && <span className="text-xs text-muted-foreground">{line.note}</span>}
                </span>
                <span className="font-mono font-medium">{displayPercent(line.share, 0)}</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
