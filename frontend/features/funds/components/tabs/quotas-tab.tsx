import { useState } from "react";
import { ControlNotice } from "@/shared/components/control-notice";
import { FundSection } from "@/shared/components/fund-section";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { CONTROL, OFFER_COMMISSION } from "@/shared/lib/fund-metrics";
import { quotasToControl, sellableKeepingControl } from "@/shared/lib/fund-quota";
import { managerQuotasOf, managerShareOf } from "@/shared/lib/fund-view";
import {
  displayIsoDate,
  displayMoney,
  displayMonthName,
  displayPercent,
  displayQuantity,
} from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { issuanceRows } from "../../lib/fund-issuances";
import type { FundTabActions } from "../../lib/fund-tabs";
import { DirectedIssuanceAlert } from "../directed-issuance-alert";
import { FundBuybackCard } from "../fund-buyback-card";
import { FundIssuanceCard } from "../fund-issuance-card";
import { FundManagersCard } from "../fund-managers-card";
import { FundOfferCard } from "../fund-offer-card";

type Holder = FundDetails["holders"][number];

// A comissão dos banqueiros de ofertas é 1% do captado
const OFFER_COMMISSION_RATE = 0.01;

/** O papel do cotista na gestora. */
function roleOf(fund: FundDetails, holder: Holder): string {
  if (holder.kind === "maker") return "Mercado";
  if (holder.kind === "bot") return "Bot";
  if (holder.user_id === fund.manager_user_id) return "Gestor";
  const comanager = fund.comanagers.some((item) => item.user_id === holder.user_id && item.status === "ACTIVE");
  return comanager ? "Co-gestor" : "Cotista";
}

/** O título do aviso de controle, com a dica do que é controle ao lado. */
function ControlTitle({ share }: { share: number }) {
  return (
    <span className="inline-flex items-center gap-1">
      Controle: você tem {displayPercent(share, 1)} das cotas
      <MetricHint metric={CONTROL} />
    </span>
  );
}

/** O aviso de controle: o gestor vê quanto pode vender, os outros veem quanto falta para os 50%. */
function ControlLine({ fund }: { fund: FundDetails }) {
  const total = Number(fund.quotas);
  const mine = Number(fund.my_quotas);

  if (fund.my_role === "manager") {
    const share = managerShareOf(fund);
    const sellable = fund.sellable_keeping_control
      ? Number(fund.sellable_keeping_control)
      : sellableKeepingControl(managerQuotasOf(fund), total);

    return (
      <ControlNotice keepsControl={share > 0.5} title={<ControlTitle share={share} />}>
        {share > 0.5
          ? `Dá para vender até ${displayQuantity(String(sellable))} cotas sem perder o controle.`
          : "Abaixo de 50% os outros cotistas podem juntar mais votos que você numa assembleia."}
      </ControlNotice>
    );
  }

  if (mine <= 0) return null;
  const missing = quotasToControl(mine, total);

  return (
    <ControlNotice keepsControl={missing === 0} title={<ControlTitle share={total > 0 ? mine / total : 0} />}>
      {missing > 0
        ? `Faltam ${displayQuantity(String(missing))} cotas para você passar dos 50%.`
        : "Você já passa dos 50%."}
    </ControlNotice>
  );
}

/** O card "Cotistas": quem tem as cotas, quanto valem e quem vota na assembleia. */
function HoldersCard({ fund }: { fund: FundDetails }) {
  const nav = fund.nav === null ? null : Number(fund.nav);
  const total = fund.holders.reduce((sum, holder) => sum + Number(holder.quotas), 0);

  return (
    <FundSection title="Cotistas">
      <div className="grid gap-3">
        <ControlLine fund={fund} />
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead wrap>Cotista</TableHead>
              <TableHead>Papel</TableHead>
              <TableHead numeric>Cotas</TableHead>
              <TableHead numeric>Fatia</TableHead>
              <TableHead numeric>Vale pelo patrimônio por cota</TableHead>
              <TableHead>Vota na assembleia</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fund.holders.map((holder) => (
              <TableRow key={`${holder.kind}-${holder.user_id ?? holder.nickname}`}>
                <TableCell wrap>
                  <span className="flex items-center gap-2">
                    <PlayerAvatar
                      nickname={holder.nickname}
                      bot={holder.kind !== "player"}
                      {...(holder.color ? { color: holder.color } : {})}
                      size="sm"
                    />
                    <span className="truncate font-medium" title={holder.nickname}>
                      {holder.nickname}
                    </span>
                  </span>
                </TableCell>
                <TableCell>{roleOf(fund, holder)}</TableCell>
                <TableCell numeric>{displayQuantity(holder.quotas)}</TableCell>
                <TableCell numeric>{displayPercent(holder.share, 1)}</TableCell>
                <TableCell numeric>{nav === null ? "—" : displayMoney(Number(holder.quotas) * nav)}</TableCell>
                <TableCell>{holder.kind === "player" ? "Sim" : "Só no aumento de taxa"}</TableCell>
              </TableRow>
            ))}
            <TableRow>
              <TableCell wrap>
                <b className="font-semibold">Total</b>
              </TableCell>
              <TableCell />
              <TableCell numeric>{displayQuantity(String(total))}</TableCell>
              <TableCell numeric>{displayPercent(total > 0 ? 1 : 0, 0)}</TableCell>
              <TableCell numeric>{nav === null ? "—" : displayMoney(total * nav)}</TableCell>
              <TableCell />
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </FundSection>
  );
}

/** O resultado da oferta pública encerrada, que pode ser recolhido. */
function OfferHistory({ fund }: { fund: FundDetails }) {
  const [open, setOpen] = useState(true);
  if (fund.listed_on === null || fund.offer_closed_on === null || fund.offer_quotas === null) return null;

  const raised = Number(fund.offer_raised ?? 0);

  return (
    <FundSection
      title={`Oferta pública de ${displayMonthName(fund.offer_closed_on)}`}
      action={
        <Button size="xs" variant="outline" aria-expanded={open} onClick={() => setOpen(!open)}>
          {open ? "Recolher" : "Expandir"}
        </Button>
      }
    >
      {open && (
        <div>
          <KeyValueRow
            label="Período"
            value={`${displayIsoDate(fund.listed_on)} a ${displayIsoDate(fund.offer_closed_on)}`}
          />
          <KeyValueRow
            label="Vendido"
            value={`${displayQuantity(fund.offer_sold ?? "0")} de ${displayQuantity(fund.offer_quotas)} cotas`}
          />
          <KeyValueRow label="Captado" value={displayMoney(raised)} />
          <KeyValueRow
            label={<MetricLabel metric={OFFER_COMMISSION} />}
            value={`até ${displayMoney(raised * OFFER_COMMISSION_RATE)}`}
          />
        </div>
      )}
    </FundSection>
  );
}

/** O card "Emissões": cada vez que a gestora vendeu cotas novas e o dinheiro que entrou. */
function IssuancesCard({ fund }: { fund: FundDetails }) {
  const rows = issuanceRows(fund);
  if (rows.length === 0) return null;

  return (
    <FundSection title="Emissões">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data</TableHead>
            <TableHead>Como</TableHead>
            <TableHead numeric>Cotas</TableHead>
            <TableHead numeric>Preço por cota</TableHead>
            <TableHead numeric>Entrou na gestora</TableHead>
            <TableHead wrap>Quem comprou</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.key}>
              <TableCell variant="note">{displayIsoDate(row.day)}</TableCell>
              <TableCell>
                <span className="flex items-center gap-2">
                  {row.how}
                  <Badge variant={row.inProgress ? "success" : "secondary"} size="tag">
                    {row.inProgress ? "em andamento" : "encerrada"}
                  </Badge>
                </span>
              </TableCell>
              <TableCell numeric>{row.quotas === null ? "—" : displayQuantity(row.quotas)}</TableCell>
              <TableCell numeric>{row.price === null ? "—" : displayMoney(row.price)}</TableCell>
              <TableCell numeric>{row.amount === null ? "—" : displayMoney(row.amount)}</TableCell>
              <TableCell wrap>
                {row.buyers}
                {row.unsoldReason && <p className="text-xs text-muted-foreground">{row.unsoldReason}</p>}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </FundSection>
  );
}

type QuotasTabProps = { fund: FundDetails; userId: number; actions: FundTabActions };

/** As cotas: quem as tem, o que está em andamento (oferta, emissão, recompra) e o histórico de emissões. */
export function QuotasTab({ fund, userId, actions }: QuotasTabProps) {
  const viewer = fund.my_role !== "manager";
  const directed = fund.directed_issuance;

  return (
    <div className="grid gap-5 pt-3">
      {/* Em andamento */}
      {fund.listed_on !== null && fund.offer_closed_on === null && <FundOfferCard fund={fund} />}
      {directed && directed.buyer_user_id !== userId && (
        <DirectedIssuanceAlert fund={fund} offer={directed} isBuyer={false} />
      )}
      <FundIssuanceCard fund={fund} />
      <FundBuybackCard fund={fund} viewer={viewer} />

      {/* Cotistas */}
      <HoldersCard fund={fund} />

      {/* Gestores */}
      {(!viewer || fund.comanagers.length > 0) && (
        <FundManagersCard
          fund={fund}
          {...(viewer
            ? {}
            : {
                actions: {
                  onInvite: () => actions.open("invite"),
                  onChangeShare: actions.changeShare,
                  onRemove: actions.remove,
                },
              })}
        />
      )}

      {/* Emissões */}
      <IssuancesCard fund={fund} />
      <OfferHistory fund={fund} />
    </div>
  );
}
