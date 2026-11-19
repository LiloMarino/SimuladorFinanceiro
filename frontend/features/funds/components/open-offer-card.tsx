import type { ReactNode } from "react";
import { Info, Megaphone, ShoppingCart, TriangleAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { FundMark } from "@/shared/components/fund-mark";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Progress } from "@/shared/components/ui/progress";
import { displayMoney, displayNumericDayMonth, displayQuantity } from "@/shared/lib/utils/display";
import type { FundOffers } from "@/types";
import {
  cashFallsShort,
  cashQuotas,
  feesText,
  isSoldOut,
  openOfferBadge,
  openOfferDeadline,
  soldPercent,
} from "../lib/fund-offers";

type OpenOffer = FundOffers["open"][number];

/** A conta com que o jogador compra: a carteira pessoal, de caixa conhecido, ou a de uma gestora. */
export type OfferWallet = { kind: "personal"; cash: number | null } | { kind: "fund"; onUsePersonal: () => void };

function Figure({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="grid gap-1 border-l border-border px-4 py-3.5 first:border-l-0">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span className="font-mono text-[22px] font-semibold">{value}</span>
      <span className="text-xs text-muted-foreground">{note}</span>
    </div>
  );
}

function Note({ children }: { children: ReactNode }) {
  return (
    <Badge variant="note" size="note">
      <Info />
      {children}
    </Badge>
  );
}

/** O texto do que aconteceu com a venda: a sobra depois da preferência ou a venda esgotada antes do prazo. */
function stateNote(offer: OpenOffer): string | null {
  if (isSoldOut(offer)) {
    const sold = `As ${displayQuantity(offer.quotas)} cotas foram vendidas.`;
    return offer.kind === "initial"
      ? `${sold} A ${offer.ticker} passa a negociar na renda variável em ${displayNumericDayMonth(offer.ends_on)}.`
      : sold;
  }
  if (offer.kind === "leftover" && offer.preference_ends_on !== null && offer.preference_bought !== null) {
    return `Os cotistas da ${offer.name} tiveram a preferência até ${displayNumericDayMonth(offer.preference_ends_on)} e compraram ${displayQuantity(offer.preference_bought)} cotas. A sobra vale para todos.`;
  }
  return null;
}

type OpenOfferCardProps = { offer: OpenOffer; wallet: OfferWallet };

/** Uma venda aberta a qualquer investidor: preço fixo, quanto resta, o prazo e os botões que levam à compra. */
export function OpenOfferCard({ offer, wallet }: OpenOfferCardProps) {
  const manager = offer.manager_nickname ? ` · gerida por ${offer.manager_nickname}` : "";
  const fresh = offer.kind === "initial" ? " · gestora nova" : "";
  const note = stateNote(offer);
  const shortOfCash =
    wallet.kind === "personal" && wallet.cash !== null && cashFallsShort(offer, wallet.cash) ? wallet.cash : null;

  return (
    <div className="grid overflow-clip rounded-xl border border-border">
      {/* Gestora e etapa */}
      <div className="flex items-center gap-3 px-5 py-4">
        <FundMark name={offer.name} size="md" />
        <div className="grid min-w-0">
          <b className="font-semibold">{offer.name}</b>
          <span className="text-xs text-muted-foreground">
            {offer.ticker}
            {manager}
            {fresh}
          </span>
        </div>
        <Badge className="ml-auto" variant={isSoldOut(offer) ? "secondary" : "info"} size="tag">
          {!isSoldOut(offer) && offer.kind === "initial" && <Megaphone />}
          {openOfferBadge(offer)}
        </Badge>
      </div>

      {/* Preço, o que resta e o prazo */}
      <div className="grid grid-cols-3 border-t border-border">
        <Figure label="Preço fixo por cota" value={displayMoney(offer.price)} note="o mesmo para todos" />
        <Figure
          label="Ainda à venda"
          value={displayQuantity(offer.remaining)}
          note={`de ${displayQuantity(offer.quotas)} cotas`}
        />
        <Figure label="Vai até" value={displayNumericDayMonth(offer.ends_on)} note={openOfferDeadline(offer)} />
      </div>

      <div className="grid gap-3 px-5 pt-4 pb-4">
        <Progress size="md" indicatorTone="fund" value={soldPercent(offer)} aria-label="Cotas já vendidas" />
        <p className="text-xs text-muted-foreground">{feesText(offer)}</p>
        {note !== null &&
          (isSoldOut(offer) ? <Note>{note}</Note> : <p className="text-xs text-muted-foreground">{note}</p>)}
        {wallet.kind === "fund" && (
          <Note>As cotas entram e saem da sua carteira pessoal. Volte para ela para comprar.</Note>
        )}
        {shortOfCash !== null && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertTitle>
              Seu caixa compra até{" "}
              {displayQuantity(String(cashQuotas(shortOfCash, Number(offer.price), Number(offer.remaining))))} cotas da{" "}
              {offer.name}.
            </AlertTitle>
            <AlertDescription>
              A quantidade da boleta para nesse número; vender outro ativo libera mais.
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Ações */}
      <div className="flex flex-wrap justify-end gap-2 border-t border-border px-5 py-3">
        {wallet.kind === "fund" && (
          <Button variant="outline" size="sm" onClick={wallet.onUsePersonal}>
            Voltar para a carteira pessoal
          </Button>
        )}
        <Button variant="outline" size="sm" nativeButton={false} render={<Link to={`/funds/${offer.fund_id}`} />}>
          Ver a gestora
        </Button>
        <Button variant="fund" size="sm" nativeButton={false} render={<Link to={`/variable-income/${offer.ticker}`} />}>
          <ShoppingCart />
          Comprar na oferta
        </Button>
      </div>
    </div>
  );
}
