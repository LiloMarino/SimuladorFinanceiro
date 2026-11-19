import { Lock } from "lucide-react";
import { Link } from "react-router-dom";
import { FundMark } from "@/shared/components/fund-mark";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { TableCell, TableRow } from "@/shared/components/ui/table";
import { premium } from "@/shared/lib/fund-quota";
import { fundStage } from "@/shared/lib/fund-view";
import {
  displayDayMonth,
  displayMoney,
  displayMonthSlashYear,
  displayPercent,
  displayQuantity,
} from "@/shared/lib/utils/display";
import type { FundRoomItem } from "@/types";
import { operates, roomNetWorth, roomShareOf } from "../lib/fund-room";

const STAGE = {
  closed: { label: "Fechada", variant: "secondary" },
  offer: { label: "Oferta aberta", variant: "info" },
  listed: { label: "Negociada", variant: "success" },
} as const;

/** O texto menor sob o nome: o ticker e o papel do jogador (ou de quem gere) na gestora. */
function roleLine(fund: FundRoomItem, userId: number): string {
  if (fund.manager_user_id === userId) {
    if (fund.frozen_until) {
      return `${fund.ticker} · congelada até o fim do mandato, em ${displayMonthSlashYear(fund.frozen_until)}`;
    }
    const since =
      fund.manager_since && fund.manager_user_id !== fund.founder_user_id
        ? ` desde ${displayDayMonth(fund.manager_since)}`
        : "";
    const names = fund.comanager_nicknames;
    const co = names.length > 0 ? ` · ${names.length === 1 ? "co-gestora" : "co-gestoras"} ${names.join(", ")}` : "";
    return `${fund.ticker} · você é a gestora${since}${co}`;
  }
  const parts = [fund.ticker];
  if (fund.manager_nickname) {
    parts.push(`gerida por ${fund.manager_nickname}${fund.frozen_until ? ", na presidência" : ""}`);
  }
  if (fund.i_comanage) parts.push("você é co-gestora");
  if (Number(fund.my_quotas) > 0) parts.push("você é cotista");
  return parts.join(" · ");
}

function Sub({ children }: { children: React.ReactNode }) {
  return <span className="block font-sans text-xs text-muted-foreground">{children}</span>;
}

/** O que a coluna de patrimônio diz sob o valor: as cotas, ou como anda a oferta. */
function netWorthNote(fund: FundRoomItem, stage: ReturnType<typeof fundStage>) {
  if (stage === "offer" && fund.offer_quotas !== null && fund.offer_remaining !== null) {
    const sold = Number(fund.offer_quotas) - Number(fund.offer_remaining);
    return `${displayQuantity(String(sold))} de ${displayQuantity(fund.offer_quotas)} vendidas`;
  }
  const quotas = `${displayQuantity(fund.quotas)} cotas`;
  return stage === "closed" ? `${quotas}, todas do gestor` : quotas;
}

/** O preço e a nota sob ele: o ágio sobre o patrimônio por cota, o preço fixo da oferta ou a gestora que ainda não negocia. */
function priceCell(fund: FundRoomItem, stage: ReturnType<typeof fundStage>) {
  if (stage === "offer" && fund.offer_price !== null) {
    return {
      value: displayMoney(fund.offer_price),
      note: fund.offer_ends_on ? `preço fixo até ${displayDayMonth(fund.offer_ends_on)}` : null,
    };
  }
  if (fund.price === null) return { value: "—", note: stage === "closed" ? "ainda não negocia" : null };
  if (fund.nav === null) return { value: displayMoney(fund.price), note: null };
  const gap = premium(Number(fund.price), Number(fund.nav));
  const note =
    gap === 0
      ? "no patrimônio por cota"
      : `${displayPercent(Math.abs(gap), 1)} ${gap > 0 ? "acima" : "abaixo"} do patrimônio`;
  return { value: displayMoney(fund.price), note };
}

type FundRoomRowProps = {
  fund: FundRoomItem;
  userId: number;
  /** As decisões pendentes do jogador nesta gestora */
  pendingCount: number;
};

/** Uma gestora da lista da sala: etapa, patrimônio, preço, a parte do jogador e o botão que abre a página dela. */
export function FundRoomRow({ fund, userId, pendingCount }: FundRoomRowProps) {
  const stage = fundStage(fund);
  const netWorth = roomNetWorth(fund);
  const price = priceCell(fund, stage);
  const mine = Number(fund.my_quotas);
  const managed = operates(fund, userId);
  const onLeave = fund.leave_manager_user_id === userId;
  const offerToBuy = stage === "offer" && !managed && mine === 0;

  return (
    <TableRow>
      {/* Gestora */}
      <TableCell wrap>
        <Link to={`/funds/${fund.id}`} className="flex items-center gap-2.5 hover:text-primary">
          <FundMark name={fund.name} size="md" />
          <span className="grid min-w-0">
            <b className="line-clamp-4 font-semibold break-words">{fund.name}</b>
            <span className="text-xs text-muted-foreground">{roleLine(fund, userId)}</span>
          </span>
        </Link>
      </TableCell>
      {/* Etapa */}
      <TableCell>
        <div className="flex flex-wrap gap-1.5">
          <Badge variant={STAGE[stage].variant} size="tag">
            {STAGE[stage].label}
          </Badge>
          {managed && pendingCount > 0 && (
            <Badge variant="warning" size="tag">
              {pendingCount} para decidir
            </Badge>
          )}
          {onLeave && (
            <Badge variant="note" size="tag">
              <Lock />
              volta no fim do mandato
            </Badge>
          )}
        </div>
      </TableCell>
      {/* Patrimônio */}
      <TableCell numeric>
        {netWorth === null ? "—" : displayMoney(netWorth)}
        <Sub>{netWorthNote(fund, stage)}</Sub>
      </TableCell>
      {/* Patrimônio por cota */}
      <TableCell numeric>{fund.nav === null ? "—" : displayMoney(fund.nav)}</TableCell>
      {/* Preço no mercado */}
      <TableCell numeric>
        {price.value}
        {price.note && <Sub>{price.note}</Sub>}
      </TableCell>
      {/* Sua parte */}
      <TableCell numeric>
        {mine > 0 ? displayPercent(roomShareOf(fund), 1) : "—"}
        <Sub>
          {mine > 0
            ? `${displayQuantity(fund.my_quotas)} cotas${fund.nav === null ? "" : ` · ${displayMoney(mine * Number(fund.nav))}`}`
            : "sem cotas"}
        </Sub>
      </TableCell>
      {/* Ação */}
      <TableCell numeric>
        <Button
          size="sm"
          variant={managed ? "fund" : "outline"}
          nativeButton={false}
          render={<Link to={`/funds/${fund.id}`} />}
        >
          {offerToBuy ? "Ver a oferta" : "Abrir"}
        </Button>
      </TableCell>
    </TableRow>
  );
}
